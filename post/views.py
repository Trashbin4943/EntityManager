from django.shortcuts import render, redirect
from django.http import Http404
from django.core.exceptions import EmptyResultSet
from .models import Post
from user.models import User


QUERYSETS = [
    {
        'key': 'all',
        'label': 'Post.objects.all()',
        'desc': '기본 Manager — 전체 게시글 (필터 없음)',
    },
    {
        'key': 'published',
        'label': 'Post.objects.published()',
        'desc': 'is_published=True 인 게시글만',
    },
    {
        'key': 'draft',
        'label': 'Post.objects.draft()',
        'desc': 'is_published=False 인 게시글만',
    },
    {
        'key': 'popular',
        'label': 'Post.objects.published().popular()',
        'desc': '공개글 중 view_count >= 100 (체이닝)',
    },
    {
        'key': 'by-alice',
        'label': 'Post.objects.published().by_user(alice)',
        'desc': 'alice의 공개 게시글만 (체이닝)',
    },
    {
        'key': 'recent',
        'label': 'Post.objects.published().recent(3)',
        'desc': '최근 공개 게시글 3개 (체이닝)',
    },
    {
        'key': 'manager-all',
        'label': 'Post.published.all()',
        'desc': 'PublishedManager — .all()만 해도 공개글로 제한됨',
    },
    {
        'key': 'manager-popular',
        'label': 'Post.published.popular()',
        'desc': 'PublishedManager 커스텀 메서드 — 공개글 중 인기글',
    },
]

_QS_MAP = {item['key']: item for item in QUERYSETS}


def _resolve_qs(key):
    alice = User.objects.filter(username='alice').first()
    mapping = {
        'all':            lambda: Post.objects.all(),
        'published':      lambda: Post.objects.published(),
        'draft':          lambda: Post.objects.draft(),
        'popular':        lambda: Post.objects.published().popular(min_views=100),
        'by-alice':       lambda: Post.objects.published().by_user(alice) if alice else Post.objects.none(),
        'recent':         lambda: Post.objects.published().recent(n=3),
        'manager-all':    lambda: Post.published.all(),
        'manager-popular': lambda: Post.published.popular(min_views=100),
    }
    return mapping[key]()


def seed_view(request):
    u, _ = User.objects.get_or_create(
        username='alice',
        defaults={'email': 'alice@example.com', 'password': 'pw'},
    )
    b, _ = User.objects.get_or_create(
        username='bob',
        defaults={'email': 'bob@example.com', 'password': 'pw'},
    )
    samples = [
        {'title': '[Draft] 초안 게시글',      'user': u, 'content': 'alice의 임시저장 글', 'is_published': False, 'view_count': 5},
        {'title': '[Public] 일반 공개글',      'user': u, 'content': 'alice의 공개 글',     'is_published': True,  'view_count': 40},
        {'title': '[Popular] 인기 공개글',     'user': u, 'content': 'alice의 인기 글',     'is_published': True,  'view_count': 250},
        {'title': '[Bob] Bob의 초안',          'user': b, 'content': 'bob의 임시저장 글',   'is_published': False, 'view_count': 0},
        {'title': '[Bob] Bob의 인기 공개글',   'user': b, 'content': 'bob의 인기 글',       'is_published': True,  'view_count': 150},
    ]
    for s in samples:
        Post.objects.get_or_create(title=s['title'], defaults={k: v for k, v in s.items() if k != 'title'})
    return redirect('main')


def main_view(request):
    posts = Post.objects.all()
    return render(request, 'post/main.html', {
        'posts': posts,
        'querysets': QUERYSETS,
    })


def qs_result_view(request, qs_key):
    if qs_key not in _QS_MAP:
        raise Http404
    config = _QS_MAP[qs_key]
    qs = _resolve_qs(qs_key)
    try:
        sql = str(qs.query)
    except EmptyResultSet:
        sql = '(빈 QuerySet — 결과 없음)'
    return render(request, 'post/qs_result.html', {
        'config': config,
        'posts': qs,
        'sql': sql,
        'querysets': QUERYSETS,
    })
