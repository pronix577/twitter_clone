from fastapi import FastAPI, Request, Header, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from schemas import Item
from controllers import add_tweet_to_db, get_list_tweets, delete_tweet, like_it_tweet, remove_like_tweet, following, unfollowing, get_user
from models import Tweets, Users, Follower, Like, async_session_maker, Base, engine


application = FastAPI()


@application.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_maker() as session:
        async with session.begin():
            session.add_all(
                [
                    Users(name='CEO', api_key='ceo'),
                    Users(name='Developer', api_key='dev'),
                    Users(name='Boss', api_key='boss'),
                    Users(name="Guest", api_key='guest'),
                    Users(name="Test", api_key='test'),
                    Tweets(content="i'm CEO :) мои подписчики: разработчик, мои подписки: маркетолог, босс", author_id=1),
                    Tweets(content="i'm Developer мои подписчики: сео, мои подписки: сео", author_id=2),
                    Tweets(content="i'm boss мои подписчики: сео, мои подписки: гость", author_id=3),
                    Tweets(content="Hi, I'm guest <3", author_id=4),
                    Follower(following_id=2, followers_id=1),
                    Follower(following_id=3, followers_id=1),
                    Follower(following_id=1, followers_id=2),
                    Follower(following_id=4, followers_id=3),
                    Like(tweet_id=1, user_id=1),
                    Like(tweet_id=1, user_id=2),
                ]
            )
            await session.commit()


class MyException(Exception):
    ...


@application.exception_handler(HTTPException)
async def http_general_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"result": False, "error_type": "HTTP Error", "error_message": exc.detail}
    )


@application.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: MyException):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"result": False, "error_type": "Server Error", "error_message": str(exc)}
    )


@application.exception_handler(SQLAlchemyError)
async def sql_exception_handler(request: Request, exc: SQLAlchemyError):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"result": False, "error_type": "Server Error", "error_message": str(exc)}
    )


@application.post("/api/tweets")
async def post_tweets(item: Item, api_key: str = Header(default=None)):

    body = item.dict()

    result = await add_tweet_to_db(content=body["tweet_data"], author=api_key)

    return {"result": True, "tweet_id": result}


@application.get("/api/tweets")
async def get_tweets(api_key: str = Header(default=None)):

    response = await get_list_tweets(api_key)

    return {"result": True, "tweets": response}


@application.delete("/api/tweets/{idd}")
async def delete_tweets(idd: int, api_key: str = Header(default=None)):

    response = await delete_tweet(api_key, idd)

    return {"result": response}


@application.post("/api/tweets/{idd}/likes")
async def like_it(idd: int, api_key: str = Header(default=None)):

    response = await like_it_tweet(api_key, idd)

    return {"result": response}


@application.delete("/api/tweets/{idd}/likes")
async def remove_like(idd: int, api_key: str = Header(default=None)):

    response = await remove_like_tweet(idd)

    return {"result": response}


@application.post("/api/users/{idd}/follow")
async def user_follow(idd: int, api_key: str = Header(default=None)):

    response = await following(api_key=api_key, follow_user_id=idd)

    return {"result": response}


@application.delete("/api/users/{idd}/follow")
async def user_follow(idd: int, api_key: str = Header(default=None)):

    response = await unfollowing(api_key=api_key, following_id=idd)

    return {"result": response}


@application.get("/api/users/me")
async def tweets_get(api_key: str = Header(default=None)):

    response = await get_user(api_key)

    return {"result": True, "user": response}


@application.get("/api/users/{idd}")
async def get_user_id(idd: int, api_key: str = Header(default=None)):

    response = await get_user(api_key, idd)

    return {"result": True, "user": response}
