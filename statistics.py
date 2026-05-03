import marketplace
import users

def index_page_stats():
    return {
        "location_count": marketplace.location_count(),
        "user_count": users.user_count(),
    }

def profile_page_stats(user_id):
    return {
        "user_location_count": marketplace.user_location_count(user_id),
        "user_comment_count": marketplace.user_comment_count(user_id),
        "user_creation_date": users.get_user_creation_date(user_id)
    }