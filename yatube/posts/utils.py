from django.core.paginator import Paginator


POST_ON_PAGE = 10


def paginating(request, post_list):
    paginator = Paginator(post_list, POST_ON_PAGE)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
