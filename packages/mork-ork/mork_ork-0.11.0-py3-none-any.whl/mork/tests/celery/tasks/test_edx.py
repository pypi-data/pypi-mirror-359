"""Tests for Mork Celery edx tasks."""

import logging
from unittest.mock import Mock
from uuid import uuid4

import pytest
from mongoengine.errors import OperationError
from mongoengine.queryset.visitor import Q
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from mork.celery.tasks.edx import (
    delete_edx_mongo_user,
    delete_edx_mysql_user,
    delete_edx_platform_user,
)
from mork.edx.mongo.factories import CommentFactory, CommentThreadFactory
from mork.edx.mongo.models import Comment, CommentThread
from mork.edx.mysql import crud as mysql
from mork.edx.mysql.factories.auth import EdxAuthUserFactory
from mork.exceptions import (
    UserDeleteError,
    UserNotFound,
    UserProtected,
    UserStatusError,
)
from mork.factories.users import UserFactory, UserServiceStatusFactory
from mork.models.users import DeletionStatus, ServiceName, User
from mork.schemas.users import UserRead


def test_delete_edx_platform_user(db_session, monkeypatch):
    """Test to delete user from edX platform."""
    UserServiceStatusFactory._meta.sqlalchemy_session = db_session
    UserFactory._meta.sqlalchemy_session = db_session

    # Create one user in the database
    UserFactory.create()

    # Get user from db
    user = UserRead.model_validate(db_session.scalar(select(User)))

    monkeypatch.setattr("mork.celery.tasks.edx.get_user_from_mork", lambda x: user)

    mock_delete_edx_mysql_user = Mock()
    monkeypatch.setattr(
        "mork.celery.tasks.edx.delete_edx_mysql_user", mock_delete_edx_mysql_user
    )
    mock_delete_edx_mongo_user = Mock()
    monkeypatch.setattr(
        "mork.celery.tasks.edx.delete_edx_mongo_user", mock_delete_edx_mongo_user
    )
    mock_update_status_in_mork = Mock(return_value=True)
    monkeypatch.setattr(
        "mork.celery.tasks.edx.update_status_in_mork", mock_update_status_in_mork
    )

    delete_edx_platform_user(user.id)

    mock_delete_edx_mysql_user.assert_called_once_with(email=user.email)
    mock_delete_edx_mongo_user.assert_called_once_with(username=user.username)
    mock_update_status_in_mork.assert_called_once_with(
        user_id=user.id, service=ServiceName.EDX, status=DeletionStatus.DELETED
    )


def test_delete_edx_platform_user_protected(db_session, monkeypatch):
    """Test to delete user and update its status to protected."""
    UserServiceStatusFactory._meta.sqlalchemy_session = db_session
    UserFactory._meta.sqlalchemy_session = db_session

    # Create one user in the database
    UserFactory.create()

    # Get user from db
    user = UserRead.model_validate(db_session.scalar(select(User)))

    monkeypatch.setattr("mork.celery.tasks.edx.get_user_from_mork", lambda x: user)

    mock_delete_edx_mysql_user = Mock(side_effect=UserProtected())
    monkeypatch.setattr(
        "mork.celery.tasks.edx.delete_edx_mysql_user", mock_delete_edx_mysql_user
    )
    mock_delete_edx_mongo_user = Mock()
    monkeypatch.setattr(
        "mork.celery.tasks.edx.delete_edx_mongo_user", mock_delete_edx_mongo_user
    )
    mock_update_status_in_mork = Mock(return_value=True)
    monkeypatch.setattr(
        "mork.celery.tasks.edx.update_status_in_mork", mock_update_status_in_mork
    )

    delete_edx_platform_user(user.id)

    mock_delete_edx_mysql_user.assert_called_once_with(email=user.email)
    mock_delete_edx_mongo_user.assert_called_once_with(username=user.username)
    mock_update_status_in_mork.assert_called_once_with(
        user_id=user.id, service=ServiceName.EDX, status=DeletionStatus.PROTECTED
    )


def test_delete_edx_platform_user_invalid_user(monkeypatch):
    """Test to delete user from edX platform with an invalid user."""

    monkeypatch.setattr("mork.celery.tasks.edx.get_user_from_mork", lambda x: None)

    mock_delete_edx_mysql_user = Mock()
    monkeypatch.setattr(
        "mork.celery.tasks.edx.delete_edx_mysql_user", mock_delete_edx_mysql_user
    )
    mock_delete_edx_mongo_user = Mock()
    monkeypatch.setattr(
        "mork.celery.tasks.edx.delete_edx_mongo_user", mock_delete_edx_mongo_user
    )
    mock_update_status_in_mork = Mock(return_value=True)
    monkeypatch.setattr(
        "mork.celery.tasks.edx.update_status_in_mork", mock_update_status_in_mork
    )

    nonexistent_id = uuid4().hex
    with pytest.raises(
        UserNotFound, match=f"User {nonexistent_id} could not be retrieved from Mork"
    ):
        delete_edx_platform_user(nonexistent_id)

    mock_delete_edx_mysql_user.assert_not_called()
    mock_delete_edx_mongo_user.assert_not_called()
    mock_update_status_in_mork.assert_not_called()


def test_delete_edx_platform_user_protected_status(db_session, monkeypatch):
    """Test to delete user from edX platform with a status PROTECTED."""
    UserServiceStatusFactory._meta.sqlalchemy_session = db_session
    UserFactory._meta.sqlalchemy_session = db_session

    # Create one user in the database that is protected on edx
    UserFactory.create(
        service_statuses={ServiceName.EDX: DeletionStatus.PROTECTED},
    )

    # Get user from db
    user = UserRead.model_validate(db_session.scalar(select(User)))

    monkeypatch.setattr("mork.celery.tasks.edx.get_user_from_mork", lambda x: user)

    mock_delete_edx_mysql_user = Mock()
    monkeypatch.setattr(
        "mork.celery.tasks.edx.delete_edx_mysql_user", mock_delete_edx_mysql_user
    )
    mock_delete_edx_mongo_user = Mock()
    monkeypatch.setattr(
        "mork.celery.tasks.edx.delete_edx_mongo_user", mock_delete_edx_mongo_user
    )
    mock_update_status_in_mork = Mock(return_value=True)
    monkeypatch.setattr(
        "mork.celery.tasks.edx.update_status_in_mork", mock_update_status_in_mork
    )

    delete_edx_platform_user(user.id)

    mock_delete_edx_mysql_user.assert_not_called()
    mock_delete_edx_mongo_user.assert_not_called()
    mock_update_status_in_mork.assert_not_called()


def test_delete_edx_platform_user_invalid_status(db_session, monkeypatch):
    """Test to delete user from edX platform with an invalid status."""
    UserServiceStatusFactory._meta.sqlalchemy_session = db_session
    UserFactory._meta.sqlalchemy_session = db_session

    # Create one user in the database that is protected on edx
    UserFactory.create(
        service_statuses={ServiceName.EDX: DeletionStatus.DELETED},
    )

    # Get user from db
    user = UserRead.model_validate(db_session.scalar(select(User)))

    monkeypatch.setattr("mork.celery.tasks.edx.get_user_from_mork", lambda x: user)

    mock_delete_edx_mysql_user = Mock()
    monkeypatch.setattr(
        "mork.celery.tasks.edx.delete_edx_mysql_user", mock_delete_edx_mysql_user
    )
    mock_delete_edx_mongo_user = Mock()
    monkeypatch.setattr(
        "mork.celery.tasks.edx.delete_edx_mongo_user", mock_delete_edx_mongo_user
    )
    mock_update_status_in_mork = Mock(return_value=True)
    monkeypatch.setattr(
        "mork.celery.tasks.edx.update_status_in_mork", mock_update_status_in_mork
    )

    with pytest.raises(
        UserStatusError,
        match=f"User {user.id} cannot be deleted. Status: DeletionStatus.DELETED",
    ):
        delete_edx_platform_user(user.id)

    mock_delete_edx_mysql_user.assert_not_called()
    mock_delete_edx_mongo_user.assert_not_called()
    mock_update_status_in_mork.assert_not_called()


def test_delete_edx_platform_user_failed_delete(db_session, monkeypatch):
    """Test to delete user from edX platform with a failed delete."""
    UserServiceStatusFactory._meta.sqlalchemy_session = db_session
    UserFactory._meta.sqlalchemy_session = db_session

    # Create one user in the database that is already deleted on edx
    UserFactory.create()

    # Get user from db
    user = UserRead.model_validate(db_session.scalar(select(User)))

    monkeypatch.setattr("mork.celery.tasks.edx.get_user_from_mork", lambda x: user)

    mock_delete_edx_mysql_user = Mock(side_effect=UserDeleteError("An error occurred"))
    monkeypatch.setattr(
        "mork.celery.tasks.edx.delete_edx_mysql_user", mock_delete_edx_mysql_user
    )
    mock_delete_edx_mongo_user = Mock()
    monkeypatch.setattr(
        "mork.celery.tasks.edx.delete_edx_mongo_user", mock_delete_edx_mongo_user
    )

    with pytest.raises(UserDeleteError, match="An error occurred"):
        delete_edx_platform_user(user.id)

    mock_delete_edx_mysql_user = Mock()
    monkeypatch.setattr(
        "mork.celery.tasks.edx.delete_edx_mysql_user", mock_delete_edx_mysql_user
    )
    mock_delete_edx_mongo_user = Mock(side_effect=UserDeleteError("An error occurred"))
    monkeypatch.setattr(
        "mork.celery.tasks.edx.delete_edx_mongo_user", mock_delete_edx_mongo_user
    )

    with pytest.raises(UserDeleteError, match="An error occurred"):
        delete_edx_platform_user(user.id)


def test_delete_edx_platform_user_failed_status_update(db_session, monkeypatch):
    """Test to delete user from edX platform with a failed status update."""
    UserServiceStatusFactory._meta.sqlalchemy_session = db_session
    UserFactory._meta.sqlalchemy_session = db_session

    # Create one user in the database that is already deleted on edx
    UserFactory.create()

    # Get user from db
    user = UserRead.model_validate(db_session.scalar(select(User)))

    monkeypatch.setattr("mork.celery.tasks.edx.get_user_from_mork", lambda x: user)

    mock_delete_edx_mysql_user = Mock()
    monkeypatch.setattr(
        "mork.celery.tasks.edx.delete_edx_mysql_user", mock_delete_edx_mysql_user
    )
    mock_delete_edx_mongo_user = Mock()
    monkeypatch.setattr(
        "mork.celery.tasks.edx.delete_edx_mongo_user", mock_delete_edx_mongo_user
    )
    mock_update_status_in_mork = Mock(return_value=False)
    monkeypatch.setattr(
        "mork.celery.tasks.edx.update_status_in_mork", mock_update_status_in_mork
    )

    with pytest.raises(
        UserStatusError,
        match=f"Failed to update deletion status to 'deleted' for user {user.id}",
    ):
        delete_edx_platform_user(user.id)


def test_delete_edx_mysql_user(edx_mysql_db, monkeypatch):
    """Test to delete user's data from MySQL."""
    EdxAuthUserFactory._meta.sqlalchemy_session = edx_mysql_db.session
    EdxAuthUserFactory.create(email="johndoe1@example.com")
    EdxAuthUserFactory.create(email="johndoe2@example.com")

    monkeypatch.setattr(
        "mork.celery.tasks.edx.OpenEdxMySQLDB", lambda *args: edx_mysql_db
    )

    # Check both users exist on the MySQL database
    assert mysql.get_user(
        edx_mysql_db.session,
        email="johndoe1@example.com",
    )
    assert mysql.get_user(
        edx_mysql_db.session,
        email="johndoe2@example.com",
    )

    delete_edx_mysql_user(email="johndoe1@example.com")

    # Check only one remains
    assert not mysql.get_user(
        edx_mysql_db.session,
        email="johndoe1@example.com",
    )
    assert mysql.get_user(
        edx_mysql_db.session,
        email="johndoe2@example.com",
    )


def test_delete_edx_mysql_user_protected(edx_mysql_db, monkeypatch):
    """Test to delete data from MySQL for a protected user."""
    EdxAuthUserFactory._meta.sqlalchemy_session = edx_mysql_db.session
    email = "johndoe1@example.com"
    EdxAuthUserFactory.create(email=email)

    def mock_delete_user(*args, **kwargs):
        raise UserProtected("An error occurred")

    monkeypatch.setattr("mork.celery.tasks.edx.mysql.delete_user", mock_delete_user)

    with pytest.raises(UserProtected, match="An error occurred"):
        delete_edx_mysql_user(email=email)

    # Check the user still exists on the edX MySQL database
    assert mysql.get_user(
        edx_mysql_db.session,
        email="johndoe1@example.com",
    )


def test_delete_edx_mysql_user_not_found(edx_mysql_db, monkeypatch, caplog):
    """Test that deleting a nonexistent user from MySQL should silently return."""

    monkeypatch.setattr(
        "mork.celery.tasks.edx.OpenEdxMySQLDB", lambda *args: edx_mysql_db
    )

    with caplog.at_level(logging.INFO):
        delete_edx_mysql_user(email="johndoe@example.com")

    assert (
        "mork.celery.tasks.edx",
        logging.INFO,
        "Skipping MySQL deletion : User does not exist",
    ) in caplog.record_tuples


def test_delete_edx_mysql_user_with_failure(edx_mysql_db, monkeypatch):
    """Test to delete user's data from MySQL with a commit failure."""
    EdxAuthUserFactory._meta.sqlalchemy_session = edx_mysql_db.session
    email = "johndoe1@example.com"
    EdxAuthUserFactory.create(email=email)

    def mock_session_commit():
        raise SQLAlchemyError("An error occurred")

    edx_mysql_db.session.commit = mock_session_commit
    monkeypatch.setattr(
        "mork.celery.tasks.edx.OpenEdxMySQLDB", lambda *args: edx_mysql_db
    )

    with pytest.raises(
        UserDeleteError,
        match="Failed to delete user from edX MySQL",
    ):
        delete_edx_mysql_user(email=email)


def test_delete_edx_mongo_user(edx_mongo_db, monkeypatch):
    """Test to delete user's data from MongoDB."""
    # Create one comment and one thread for two different users
    user_1 = "Johndoe1"
    CommentFactory.create(author_username=user_1)
    CommentThreadFactory.create(author_username=user_1)
    user_2 = "Johndoe2"
    CommentFactory.create(author_username=user_2)
    CommentThreadFactory.create(author_username=user_2)

    edx_mongo_db.disconnect = lambda: None
    monkeypatch.setattr(
        "mork.celery.tasks.edx.OpenEdxMongoDB", lambda *args: edx_mongo_db
    )

    # Check both users have comments in the MongoDB database
    assert Comment.objects(Q(author_username=user_1)).all().count() == 1
    assert CommentThread.objects(Q(author_username=user_1)).all().count() == 1
    assert Comment.objects(Q(author_username=user_2)).all().count() == 1
    assert CommentThread.objects(Q(author_username=user_2)).all().count() == 1

    delete_edx_mongo_user(username=user_1)

    # Check only one user remains
    assert Comment.objects(Q(author_username=user_1)).all().count() == 0
    assert CommentThread.objects(Q(author_username=user_1)).all().count() == 0
    assert Comment.objects(Q(author_username=user_2)).all().count() == 1
    assert CommentThread.objects(Q(author_username=user_2)).all().count() == 1


def test_delete_edx_mongo_user_with_failure(edx_mongo_db, monkeypatch):
    """Test to delete user's data from MongoDB with a operation failure."""
    username = "Johndoe1"
    CommentFactory.create(author_username=username)
    CommentThreadFactory.create(author_username=username)

    monkeypatch.setattr(
        "mork.celery.tasks.edx.OpenEdxMongoDB", lambda *args: edx_mongo_db
    )

    def mock_anonymize(*args):
        raise OperationError("An error occurred")

    monkeypatch.setattr(
        "mork.celery.tasks.edx.mongo.anonymize_comments", mock_anonymize
    )

    with pytest.raises(
        UserDeleteError,
        match="Failed to delete comments: An error occurred",
    ):
        delete_edx_mongo_user(username=username)
