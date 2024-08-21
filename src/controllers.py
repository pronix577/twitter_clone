from sqlalchemy import select, insert, delete, or_, join, func
from sqlalchemy.orm import selectinload, joinedload, aliased
import logging

from models import Tweets, Users, Like, Follower, async_session_maker, Base, engine

logger = logging.getLogger("twitter log")


async def get_user_id(api_key):
    async with async_session_maker() as session:
        async with session.begin():
            query = select(Users.id).where(Users.api_key == api_key)
            q = await session.execute(query)
            user_id = q.scalars().one_or_none()
            return user_id


async def add_tweet_to_db(content, author):
    async with async_session_maker() as session:
        async with session.begin():
            query_u = await session.execute(select(Users).where(Users.api_key == author))
            authors = query_u.scalars().one()

            query = insert(Tweets).values(content=content, user_id=authors.id).returning(Tweets.id)
            result = await session.execute(query)
            tweets, *_ = result.fetchone()

            await session.commit()

            return tweets


async def get_list_tweets(api_key):
    async with async_session_maker() as session:
        async with session.begin():

            user_id = await get_user_id(api_key=api_key)

            query = select(
                Tweets
            ).options(
                joinedload(Tweets.author), joinedload(Tweets.likes).joinedload(Like.user)
            ).join(
                Users, Tweets.author_id == Users.id
            ).outerjoin(
                Follower, Follower.followers_id == user_id
            ).where(
                or_(Tweets.author_id == user_id, Tweets.author_id == Follower.following_id)
            )
            q = await session.execute(query)
            tweets = q.unique().scalars().all()

            result = []
            for tweet in tweets:
                tweet_data = {
                    "id": tweet.id,
                    "content": tweet.content,
                    "attachments": [],
                    "author": {
                        "id": tweet.author.id,
                        "name": tweet.author.name
                    },
                    "likes": [
                        {"user_id": like.user.id, "name": like.user.name} for like in tweet.likes
                    ]
                }
                result.append(tweet_data)

            sort_result = sorted(result, reverse=True, key=lambda d: len(d["likes"]))

            return sort_result


async def delete_tweet(author, idd):
    async with async_session_maker() as session:
        async with session.begin():
            query = select(Tweets.user_id).where(Tweets.id == idd)
            q = await session.execute(query)
            tweet_author_id = q.scalars().one()

            user_id = await get_user_id(author)

            if tweet_author_id == user_id:
                await session.execute(delete(Tweets).where(Tweets.id == idd))
                await session.commit()
                return True
            else:
                return False


async def like_it_tweet(api_key, idd):
    async with async_session_maker() as session:
        async with session.begin():

            user_id = await get_user_id(api_key)

            new_like = Like(tweet_id=idd, user_id=user_id)

            session.add(new_like)
            await session.commit()

            return True


async def remove_like_tweet(idd):
    async with async_session_maker() as session:
        async with session.begin():
            await session.execute(delete(Like).where(Like.tweet_id == idd))
            await session.commit()
            return True


async def following(api_key, follow_user_id):
    async with async_session_maker() as session:
        async with session.begin():
            q = await session.execute(select(Users.id).where(Users.api_key == api_key))
            followers = q.scalars().one()

            new_follow = Follower(following_id=follow_user_id, followers_id=followers)

            session.add(new_follow)
            await session.commit()

            return True


async def unfollowing(api_key, following_id):
    async with async_session_maker() as session:
        async with session.begin():
            q = await session.execute(select(Users.id).where(Users.api_key == api_key))
            followers_id = q.scalars().one()

            query = delete(Follower).where(Follower.following_id == following_id).\
                where(Follower.followers_id == followers_id)
            await session.execute(query)

            await session.commit()

            return True


async def get_user(api_key, idd=None):
    async with async_session_maker() as session:
        async with session.begin():

            if idd is None:
                q = await session.execute(select(Users).where(Users.api_key == api_key))
                user = q.scalars().one_or_none()
            else:
                q = await session.execute(select(Users).where(Users.id == idd))
                user = q.scalars().one_or_none()

            query = select(
                Follower
            ).options(
                joinedload(Follower.following_f), joinedload(Follower.followers_f)
            ).where(
                or_(Follower.followers_id == user.id, Follower.following_id == user.id)
            )

            q = await session.execute(query)
            follows = q.unique().scalars().all()

            result = {
                "id": user.id,
                "name": user.name,
                "followers": [
                    {"id": follow.followers_f.id, "name": follow.followers_f.name} for follow in follows if
                    follow.followers_f.id != user.id
                ],
                "following": [
                    {"id": follow.following_f.id, "name": follow.following_f.name} for follow in follows if
                    follow.following_f.id != user.id
                ]
            }

            return result
