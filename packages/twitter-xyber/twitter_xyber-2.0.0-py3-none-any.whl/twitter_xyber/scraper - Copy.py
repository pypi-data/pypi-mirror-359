import asyncio
import json
from os import path
from playwright.sync_api import sync_playwright
import time
import re
import json
from datetime import datetime
from collections import Counter

class TwitterScraper:
    def __init__(self, headless=True, username=None, password=None):
        self.headless = headless
        self.username = username
        self.password = password
        self.browser = None

    def login(self):
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=self.headless)
            context = browser.new_context(
                viewport={"width": 1280, "height": 1024},
                default_browser_type="chromium",
            )
            page = context.new_page()
            page.goto("https://twitter.com/i/flow/login")
            page.wait_for_selector("[data-testid='google_sign_in_container']")
            time.sleep(2)
            page.fill('input[type="text"]', self.username)
            time.sleep(2)
            page.locator("//span[text()='Next']").click()
            page.wait_for_selector("[data-testid='LoginForm_Login_Button']")
            time.sleep(2)
            page.fill('input[type="password"]', self.password)
            time.sleep(2)
            page.locator("//span[text()='Log in']").click()
            time.sleep(2)
            context.storage_state(path="state.json")
            time.sleep(2)
            context.close()
            browser.close()
    
    def search_user(self, user_input: str) -> dict:
        _xhr_calls = []

        def intercept_response(response):
            if response.request.resource_type == "xhr":
                _xhr_calls.append(response)
            return response

        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=self.headless)
            context = browser.new_context(viewport={"width": 1920, "height": 1080}, storage_state="state.json")
            page = context.new_page()

            page.on("response", intercept_response)
            page.goto(f"https://twitter.com/search?q={user_input}&src=typed_query&f=user")
            page.wait_for_selector("[data-testid='cellInnerDiv']")
            time.sleep(5)

            for f in _xhr_calls:
                if re.search("SearchTimeline", f.url):
                    tweet_calls = [f]
                    break

            users = []
            for xhr in tweet_calls:
                data = xhr.json()
                search_result = data['data']['search_by_raw_query']['search_timeline']['timeline']['instructions'][1]['entries']
            
            del search_result[-2:]

            for sr in search_result:
                try:
                    legacy = sr['content']['itemContent']['user_results']['result']
                    users.append({
                        "user_id" : legacy['rest_id'],
                        "name" : legacy['legacy']['name'],
                        "screen_name" : legacy['legacy']['screen_name'],
                        "bio" : legacy['legacy']['description'],
                        "location" : legacy['legacy']['location'],
                        "followers" : legacy['legacy']['followers_count'],
                        "following" : legacy['legacy']['friends_count'],
                        "tweets" : legacy['legacy']['statuses_count'],
                        "favorites" : legacy['legacy']['favourites_count'],
                        "private" : legacy['legacy']['protected']  if 'protected' in legacy['legacy'] else False,
                        "verified" : legacy['is_blue_verified'],
                        "avatar" : legacy['legacy']['profile_image_url_https'],
                        "created" : legacy['legacy']['created_at'],
                    })
                except:
                    pass

            context.close()
            browser.close()
            return users

    def following_user(self, username: str) -> dict:
        _xhr_calls = []

        def intercept_response(response):
            if response.request.resource_type == "xhr":
                _xhr_calls.append(response)
            return response

        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=self.headless)
            context = browser.new_context(viewport={"width": 1920, "height": 1080}, storage_state="state.json")
            page = context.new_page()

            page.on("response", intercept_response)
            page.goto(f"https://twitter.com/{username}/following")
            page.wait_for_selector("[data-testid='cellInnerDiv']")
            time.sleep(5)

            for f in _xhr_calls:
                if re.search("Following", f.url):
                    following_calls = [f]
                    break

            users = []
            for xhr in following_calls:
                data = xhr.json()
                instruction = data['data']['user']['result']['timeline']['timeline']['instructions']
                following_result = next(ins['entries'] for ins in instruction if ins['type'] == 'TimelineAddEntries')

            del following_result[-2:]

            for fr in following_result:
                try:
                    legacy = fr['content']['itemContent']['user_results']['result']
                    users.append({
                        "id" : legacy['rest_id'],
                        "name" : legacy['legacy']['name'],
                        "username" : legacy['legacy']['screen_name'],
                        "followers" : legacy['legacy']['followers_count'],
                        "following" : legacy['legacy']['friends_count'],
                        "url" : '',
                        "tweets" : legacy['legacy']['statuses_count'],
                        "profile_image_url_https" : legacy['legacy']['profile_image_url_https'],
                        "created" : legacy['legacy']['created_at'],
                    })
                except:
                    pass
            
            context.close()
            browser.close()
            return users

    def followers_user(self, username: str) -> dict:
        _xhr_calls = []

        def intercept_response(response):
            if response.request.resource_type == "xhr":
                _xhr_calls.append(response)
            return response

        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=self.headless)
            context = browser.new_context(viewport={"width": 1920, "height": 1080}, storage_state="state.json")
            page = context.new_page()

            page.on("response", intercept_response)
            page.goto(f"https://twitter.com/{username}/followers")
            page.wait_for_selector("[data-testid='cellInnerDiv']")
            time.sleep(5)

            for f in _xhr_calls:
                if re.search("Followers", f.url):
                    followers_calls = [f]
                    break

            users = []
            for xhr in followers_calls:
                data = xhr.json()
                instruction = data['data']['user']['result']['timeline']['timeline']['instructions']
                followers_result = next(ins['entries'] for ins in instruction if ins['type'] == 'TimelineAddEntries')

            del followers_result[-2:]

            for fr in followers_result:
                try:
                    legacy = fr['content']['itemContent']['user_results']['result']
                    users.append({
                        "id" : legacy['rest_id'],
                        "name" : legacy['legacy']['name'],
                        "username" : legacy['legacy']['screen_name'],
                        "followers" : legacy['legacy']['followers_count'],
                        "following" : legacy['legacy']['friends_count'],
                        "url" : '',
                        "tweets" : legacy['legacy']['statuses_count'],
                        "profile_image_url_https" : legacy['legacy']['profile_image_url_https'],
                        "created" : legacy['legacy']['created_at'],
                    })
                except:
                    pass
            
            context.close()
            browser.close()
            return users

    def user_mention(self, username: str, tweet_count: int = 20) -> dict:
        _xhr_calls = []
        min_count = 20
        max_count = 100

        def intercept_response(response):
            if response.request.resource_type == "xhr":
                _xhr_calls.append(response)
            return response

        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=self.headless)
            context = browser.new_context(viewport={"width": 1800, "height": 1080}, storage_state="state.json")
            page = context.new_page()

            page.on("response", intercept_response)
            page.goto(f"https://twitter.com/{username}")
            page.wait_for_selector("[data-testid='tweet']")
            time.sleep(5)

            _prev_height = -1
            _max_scrolls = int(round(tweet_count / 20, 0)) if tweet_count >= min_count and tweet_count <= max_count else 1
            _scroll_count = 0

            tweets = []
            while _scroll_count < _max_scrolls:
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                page.wait_for_timeout(1000)
                new_height = page.evaluate("document.body.scrollHeight")
                if new_height == _prev_height:
                    break
                _prev_height = new_height
                _scroll_count += 1
                time.sleep(10)

                for f in _xhr_calls:
                    if re.search("UserTweets", f.url):
                        user_tweets_calls = [f]
                        break

                for xhr in user_tweets_calls:
                    data = xhr.json()
                    instruction = data['data']['user']['result']['timeline_v2']['timeline']['instructions']
                    tweet_result = next(ins['entries'] for ins in instruction if ins['type'] == 'TimelineAddEntries')

                del tweet_result[-2:]

                for sr in tweet_result:
                    try:
                        legacy = sr['content']['itemContent']['tweet_results']['result']['legacy']['entities']
                        tweets.append({
                            "mentions" : legacy['user_mentions'][0]['screen_name'],
                        })
                    except:
                        pass
                mention_counts = Counter(tweet['mentions'] for tweet in tweets)
                total_tweets = len(tweets)
                mention_results = []

                for mention, count in mention_counts.items():
                    percentage = (count / total_tweets) * 100 if total_tweets > 0 else 0
                    mention_results.append({
                        "user_mention": mention,
                        "count": count,
                        "percentage": percentage
                    })

            context.close()
            browser.close()
            return mention_results

    def user_hashtag(self, username: str, tweet_count: int = 20) -> dict:

        hashtags_counter = Counter()

        _xhr_calls = []
        min_count = 20
        max_count = 100

        def intercept_response(response):
            if response.request.resource_type == "xhr":
                _xhr_calls.append(response)
            return response

        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=self.headless)
            context = browser.new_context(viewport={"width": 1800, "height": 1080}, storage_state="state.json")
            page = context.new_page()

            page.on("response", intercept_response)
            page.goto(f"https://twitter.com/{username}")
            page.wait_for_selector("[data-testid='tweet']")
            time.sleep(5)

            _prev_height = -1
            _max_scrolls = int(round(tweet_count / 20, 0)) if tweet_count >= min_count and tweet_count <= max_count else 1
            _scroll_count = 0

            tweets = []
            while _scroll_count < _max_scrolls:
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                page.wait_for_timeout(1000)
                new_height = page.evaluate("document.body.scrollHeight")
                if new_height == _prev_height:
                    break
                _prev_height = new_height
                _scroll_count += 1
                time.sleep(10)

                for f in _xhr_calls:
                    if re.search("UserTweets", f.url):
                        user_tweets_calls = [f]
                        break

                for xhr in user_tweets_calls:
                    data = xhr.json()
                    instruction = data['data']['user']['result']['timeline_v2']['timeline']['instructions']
                    tweet_result = next(ins['entries'] for ins in instruction if ins['type'] == 'TimelineAddEntries')

                del tweet_result[-2:]

                for sr in tweet_result:
                    try:
                        legacy = sr['content']['itemContent']['tweet_results']['result']['legacy']['entities']
                        if legacy['hashtags']:
                            hashtags_data = legacy['hashtags']
                            hashtags_text = [hashtag['text'] for hashtag in hashtags_data]
                            hashtags_counter.update(hashtags_text)
                    except:
                        pass
                total_tweets = sum(hashtags_counter.values())
                hashtags_results = []

                for hashtag, count in hashtags_counter.items():
                    percentage = (count / total_tweets) * 100 if total_tweets > 0 else 0
                    hashtags_results.append({
                        "hastags": hashtag,
                        "count": count,
                        "percentage": percentage
                    })

            context.close()
            browser.close()
            return hashtags_results

    def timeline_tweet(self, username: str, tweet_count: int = 80) -> dict:
        _xhr_calls = []
        min_count = 20
        max_count = 100

        def intercept_response(response):
            if response.request.resource_type == "xhr":
                _xhr_calls.append(response)
            return response

        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=self.headless)
            context = browser.new_context(viewport={"width": 1800, "height": 1080}, storage_state="state.json")
            page = context.new_page()

            page.on("response", intercept_response)
            page.goto(f"https://twitter.com/{username}")
            page.wait_for_selector("[data-testid='tweet']")
            time.sleep(5)

            _prev_height = -1
            _max_scrolls = int(round(tweet_count / 20, 0)) if tweet_count >= min_count and tweet_count <= max_count else 1
            _scroll_count = 0

            timeline = []
            hashtags_data = {}
            mentions_data = {}
            print('max scroll:', _max_scrolls)
            while _scroll_count < _max_scrolls:
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                page.wait_for_timeout(1000)
                new_height = page.evaluate("document.body.scrollHeight")
                if new_height == _prev_height:
                    break
                _prev_height = new_height
                _scroll_count += 1
                time.sleep(5)

                user_tweets_calls = []
                for f in _xhr_calls:
                    if re.search("UserTweets", f.url):
                        user_tweets_calls.append(f)
                        

                for xhr in user_tweets_calls:
                    data = xhr.json()
                    instruction = data['data']['user']['result']['timeline_v2']['timeline']['instructions']
                    tweet_result = next(ins['entries'] for ins in instruction if ins['type'] == 'TimelineAddEntries')

                del tweet_result[-2:]

                for tr in tweet_result:
                    try:
                        if any("tweet" in s for s in tr['entryId'].split("-")):
                            legacy = tr['content']['itemContent']['tweet_results']['result']['legacy']
                            view = tr['content']['itemContent']['tweet_results']['result']['views']
                            core =  tr['content']['itemContent']['tweet_results']['result']['core']['user_results']['result']['legacy']

                            hashtags = re.findall(r'#(\w+)', legacy['full_text'])
                            mentions = re.findall(r'@(\w+)', legacy['full_text'])

                            for hashtag in hashtags:
                                hashtags_data.setdefault(hashtag, {"count": 0, "percentage": 0})
                                hashtags_data[hashtag]["count"] += 1

                            for mention in mentions:
                                mentions_data.setdefault(mention, {"count": 0, "percentage": 0})
                                mentions_data[mention]["count"] += 1

                            # Tambahkan kondisi untuk menangani tweet tanpa media
                            if 'entities' in legacy and 'media' in legacy['entities'] and legacy['entities']['media']:
                                if legacy['entities']['media'][0]['type'] == 'video':
                                    mediainf = legacy['entities']['media'][0]['video_info']['variants'][1]['url']
                                elif legacy['entities']['media'][0]['type'] == 'photo':
                                    mediainf = legacy['entities']['media'][0]['media_url_https']
                                else:
                                    mediainf = ""
                            else:
                                mediainf = ""

                            follower = int(core['followers_count'])
                            views = int(view['count'])
                            like = int(legacy['favorite_count'])
                            retweet = int(legacy['retweet_count'])
                            reply = int(legacy['reply_count'])
                            quote = int(legacy['quote_count'])
                            dateTweet = legacy['created_at']
                            dateConvert = datetime.strptime(dateTweet, "%a %b %d %H:%M:%S %z %Y")
                            iso8601_date_str = dateConvert.isoformat()
                            engagement = ((views + like + retweet + reply + quote) / follower) * 100
                            urlTweet = f"https://twitter.com/{username}/status/{legacy['id_str']}"
                            timeline.append({
                                "id": legacy['id_str'],
                                "user_id": legacy['user_id_str'],
                                "date": iso8601_date_str,
                                "tweets": legacy['full_text'],
                                "screen_name": core['screen_name'],
                                "retweet": legacy['retweet_count'],
                                "replies": legacy['reply_count'],
                                "link_media": mediainf,
                                "likes": legacy['favorite_count'],
                                "link": legacy['entities']['media'][0]['url'] if 'entities' in legacy and 'media' in legacy['entities'] else urlTweet,
                                "views" : views,
                                "quote" : quote,
                                "engagement" : engagement,
                                "hashtags": hashtags,
                                "mentions": mentions,
                                "source": tr['content']['itemContent']['tweet_results']['result']['source']
                            })
                    except:
                        pass

                # Bersihkan _xhr_calls setelah mengumpulkan data dari setiap scroll
                # _xhr_calls = []
                # total_tweets = len(timeline)
                total_hashtags = sum(data["count"] for data in hashtags_data.values())
                total_mentions = sum(data["count"] for data in mentions_data.values())


                for hashtag, data in hashtags_data.items():
                    data["percentage"] = (data["count"] / total_hashtags) * 100 if total_hashtags > 0 else 0

                for mention, data in mentions_data.items():
                    data["percentage"] = (data["count"] / total_mentions) * 100 if total_mentions > 0 else 0

                hashtags_result = [{"hashtags": hashtag, "count": data["count"], "percentage": data["percentage"]} for hashtag, data in hashtags_data.items()]
                mentions_result = [{"user_mention": mention, "count": data["count"], "percentage": data["percentage"]} for mention, data in mentions_data.items()]

            context.close()
            browser.close()
            # return timeline
            return {"timelines": timeline, "hashtags": hashtags_result, "mentions": mentions_result}

if __name__ == "__main__":
    # Create an instance of the TwitterScraper class with desired parameters
    twitter_bot = TwitterScraper(headless=False, username='username', password='password')
    # twitter_bot.login()

    # Call the login method to execute the login process
    # twitter_bot.login()
    result = twitter_bot.timeline_tweet("username")
    print(json.dumps(result["timelines"], indent=2))
    print(json.dumps(result["hashtags"], indent=2))
    print(json.dumps(result["mentions"], indent=2))

