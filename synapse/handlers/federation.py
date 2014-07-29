# -*- coding: utf-8 -*-
"""Contains handlers for federation events."""

from ._base import BaseHandler

from synapse.api.events.room import InviteJoinEvent, RoomMemberEvent
from synapse.api.constants import Membership
from synapse.util.logutils import log_function

from twisted.internet import defer

import logging


logger = logging.getLogger(__name__)


class FederationHandler(BaseHandler):

    """Handles events that originated from federation."""

    @log_function
    @defer.inlineCallbacks
    def on_receive(self, event, is_new_state):
        if event.type == InviteJoinEvent.TYPE:
            # If we receive an invite/join event then we need to join the
            # sender to the given room.
            # TODO: We should probably auth this or some such
            content = {"membership": Membership.JOIN}
            new_event = self.event_factory.create_event(
                etype=RoomMemberEvent.TYPE,
                target_user_id=event.user_id,
                room_id=event.room_id,
                user_id=event.user_id,
                membership=Membership.JOIN,
                content=content
            )

            yield self.hs.get_handlers().room_member_handler.change_membership(
                new_event,
                True
            )

        else:
            with (yield self.room_lock.lock(event.room_id)):
                store_id = yield self.store.persist_event(event)

            yield self.notifier.on_new_event(event, store_id)
