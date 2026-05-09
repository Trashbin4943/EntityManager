from django.db import models


# ─────────────────────────────────────────────────────────────────────────────
# 실습 1: Custom QuerySet
#   - QuerySet 메서드를 정의해두면 체이닝(.published().popular())이 가능해진다.
#   - Manager와 함께 쓸 때 as_manager()로 곧바로 Manager로 변환할 수 있다.
# ─────────────────────────────────────────────────────────────────────────────
class PostQuerySet(models.QuerySet):

    def published(self):
        """공개된 게시글만 반환"""
        return self.filter(is_published=True)

    def draft(self):
        """임시저장(비공개) 게시글만 반환"""
        return self.filter(is_published=False)

    def popular(self, min_views=100):
        """조회수가 min_views 이상인 게시글 반환"""
        return self.filter(view_count__gte=min_views)

    def by_user(self, user):
        """특정 사용자의 게시글만 반환"""
        return self.filter(user=user)
    

    def recent(self, n=5):
        """최근 n개의 게시글 반환"""
        return self.order_by('-created_at')[:n]


# ─────────────────────────────────────────────────────────────────────────────
# 실습 2: Custom Manager
#   - Manager는 DB 쿼리의 진입점(Post.objects)이다.
#   - get_queryset()을 오버라이드하면 기본 QuerySet 자체를 바꿀 수 있다.
#   - QuerySet의 메서드를 Manager에서도 쓰려면 from_queryset()을 사용한다.
# ─────────────────────────────────────────────────────────────────────────────

# 방법 A: QuerySet → Manager 변환 (체이닝 + Manager 메서드 모두 사용 가능)
PostManager = models.Manager.from_queryset(PostQuerySet)


# 방법 B: Manager를 직접 작성 (get_queryset 오버라이드로 기본 범위 제한)
class PublishedManager(models.Manager):
    """Post.published.all() 호출 시 항상 공개 게시글만 반환하는 Manager"""

    def get_queryset(self):
        return PostQuerySet(self.model, using=self._db).published()

    def popular(self, min_views=100):
        return self.get_queryset().popular(min_views)


# ─────────────────────────────────────────────────────────────────────────────
# Post 모델
#   - objects  : 기본 Manager (QuerySet 메서드 전부 사용 가능)
#   - published: 공개 게시글만 다루는 전용 Manager
#
# 실습 포인트
#   Post.objects.all()              → 전체 게시글
#   Post.objects.published()        → 공개 게시글
#   Post.objects.published().popular() → 공개 + 인기 (체이닝)
#   Post.published.all()            → PublishedManager (기본이 공개글)
#   Post.published.popular()        → 공개 + 인기
# ─────────────────────────────────────────────────────────────────────────────
class Post(models.Model):
    title = models.CharField(max_length=200)
    user = models.ForeignKey('user.User', on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    # 실습을 위해 추가한 필드
    is_published = models.BooleanField(default=False)
    view_count = models.IntegerField(default=0)

    # Manager 등록: 첫 번째로 선언된 Manager가 기본(default) Manager가 된다.
    objects = PostManager()       # 기본 Manager (메서드 체이닝 가능)
    published = PublishedManager()  # 공개 게시글 전용 Manager

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title
