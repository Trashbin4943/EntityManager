# Django Custom Manager / QuerySet 실습

Django의 Custom QuerySet과 Custom Manager를 직접 실행하며 학습하는 실습 프로젝트입니다.

## 사전 요구사항

- Python 3.11 이상
- pip
- `.env` 파일

---

## 시작하기

### 1. 저장소 클론

```bash
git clone <저장소 URL>
cd blog
```

### 2. 패키지 설치

```bash
pip install -r requirements.txt
```

### 3. 환경변수 설정

사전에 보내드린 `.env` 파일을 프로젝트 루트(`manage.py`와 같은 위치)에 배치합니다.

```
blog/
├── manage.py
├── .env          ← 여기에 위치
├── blog/
├── post/
└── user/
```

`.env` 파일 형식은 다음과 같습니다.

```
SECRET_KEY=...
DB_NAME=...
DB_USER=...
DB_PASSWORD=...
DB_HOST=...
DB_PORT=...
```

### 4. 서버 실행

```bash
python manage.py runserver
```

브라우저에서 `http://127.0.0.1:8000/posts/` 접속

---

## 사용 방법

### 샘플 데이터 삽입

처음 실행 시 DB가 비어 있습니다. 메인 페이지의 **[샘플 데이터 Seed]** 버튼을 클릭하거나 아래 URL에 접속합니다.

```
http://127.0.0.1:8000/posts/seed/
```

삽입되는 데이터:

| title                   | user  | is_published | view_count |
| ----------------------- | ----- | ------------ | ---------- |
| [Draft] 초안 게시글     | alice | False        | 5          |
| [Public] 일반 공개글    | alice | True         | 40         |
| [Popular] 인기 공개글   | alice | True         | 250        |
| [Bob] Bob의 초안        | bob   | False        | 0          |
| [Bob] Bob의 인기 공개글 | bob   | True         | 150        |

### QuerySet 실행

메인 페이지(`/posts/`)에서 각 QuerySet 버튼을 클릭하면 해당 조건의 결과와 실행된 SQL을 확인할 수 있습니다.

| URL                          | QuerySet                                  | 설명                       |
| ---------------------------- | ----------------------------------------- | -------------------------- |
| `/posts/qs/all/`             | `Post.objects.all()`                      | 전체 게시글                |
| `/posts/qs/published/`       | `Post.objects.published()`                | 공개 게시글                |
| `/posts/qs/draft/`           | `Post.objects.draft()`                    | 임시저장 게시글            |
| `/posts/qs/popular/`         | `Post.objects.published().popular()`      | 공개 + 조회수 100 이상     |
| `/posts/qs/by-alice/`        | `Post.objects.published().by_user(alice)` | alice의 공개 게시글        |
| `/posts/qs/recent/`          | `Post.objects.published().recent(3)`      | 최근 공개 게시글 3개       |
| `/posts/qs/manager-all/`     | `Post.published.all()`                    | PublishedManager 기본 조회 |
| `/posts/qs/manager-popular/` | `Post.published.popular()`                | PublishedManager 인기글    |

---

## 프로젝트 구조

```
blog/
├── blog/
│   ├── settings.py     # 프로젝트 설정
│   └── urls.py         # 루트 URL
├── post/
│   ├── models.py       # PostQuerySet, PostManager, PublishedManager, Post
│   ├── views.py        # 메인/결과 뷰
│   ├── urls.py         # /posts/ 하위 URL
│   └── templates/post/
│       ├── main.html
│       └── qs_result.html
├── user/
│   └── models.py       # User 모델
├── manage.py
├── requirements.txt
└── .env                # git 미포함 — 별도 수령
```

## 핵심 학습 포인트

**`post/models.py`** 에 정의된 내용을 중심으로 실습합니다.

```python
# Custom QuerySet — 메서드 체이닝 가능
class PostQuerySet(models.QuerySet):
    def published(self): ...
    def draft(self): ...
    def popular(self, min_views=100): ...
    def by_user(self, user): ...
    def recent(self, n=5): ...

# 방법 A: QuerySet → Manager 변환
PostManager = models.Manager.from_queryset(PostQuerySet)

# 방법 B: Manager 직접 작성 (get_queryset 오버라이드)
class PublishedManager(models.Manager):
    def get_queryset(self):
        return PostQuerySet(self.model, using=self._db).published()
```
