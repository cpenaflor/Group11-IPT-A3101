from rest_framework.pagination import PageNumberPagination

# This class defines a custom pagination scheme for the news feed, 
# allowing clients to specify the page size and ensuring that it does not exceed a maximum limit.
class NewsFeedPagination(PageNumberPagination):
    # The default number of items per page is set to 5, but clients can override this by using the 'page_size' query parameter.
    page_size = 5

    # The name of the query parameter that clients can use to specify the page size is 'page_size'.
    page_size_query_param = 'page_size'

    # The maximum number of items that can be returned in a single page is set to 50, preventing clients from requesting excessively large pages.
    max_page_size = 50 