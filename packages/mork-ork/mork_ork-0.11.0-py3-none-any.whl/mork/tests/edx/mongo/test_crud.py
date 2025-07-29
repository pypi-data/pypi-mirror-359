"""Tests of the MongoDB related CRUD functions."""

from mork.conf import settings
from mork.edx.mongo import crud
from mork.edx.mongo.factories import CommentFactory, CommentThreadFactory
from mork.edx.mongo.models import Comment, CommentThread


def test_edx_mongo_crud_anonymize_comments(edx_mongo_db):
    """Test the `anonymize_comments` method."""
    username = "JohnDoe"
    CommentFactory.create_batch(3, author_username=username)
    CommentThreadFactory.create_batch(4, author_username=username)

    assert Comment.objects(author_username=username).count() == 3
    assert CommentThread.objects(author_username=username).count() == 4

    count = crud.anonymize_comments(username)

    assert count == 7
    comment = Comment.objects().first()
    assert comment.author_username == "[deleted]"
    assert comment.body == "[deleted]"
    assert comment.author_id == settings.EDX_FORUM_PLACEHOLDER_USER_ID
    assert comment.anonymous

    comment_thread = CommentThread.objects().first()
    assert comment_thread.author_username == "[deleted]"
    assert comment_thread.title == "[deleted]"
    assert comment_thread.body == "[deleted]"
    assert comment_thread.author_id == settings.EDX_FORUM_PLACEHOLDER_USER_ID
    assert comment_thread.anonymous
