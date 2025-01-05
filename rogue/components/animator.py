from os.path import join

import pygame

from rogue.enums import AnimState


class Animator:
    def __init__(self, character_name: str, anim_frame_length: float = 0.08, animation_length: int = 4):
        self.char_name = character_name
        self.anim_len = animation_length
        self.states = {
            AnimState.IDLE: [pygame.image.load(
                join("resources", "character", character_name, "idle", f"{character_name}_{i+1}.png")).convert_alpha() for i in range(self.anim_len)],
            AnimState.RUN: [pygame.image.load(
                join("resources", "character", character_name, "run", f"{character_name}_{i+1}.png")).convert_alpha() for i in range(self.anim_len)]
        }
        self.anim_idx = 0
        self.anim_timer = 0
        self.anim_frame_length = anim_frame_length
        self.current_state = AnimState.IDLE
        self.next_queued_animation = AnimState.NONE

    def get_current_image(self) -> pygame.surface.Surface:
        return self.states[self.current_state][self.anim_idx]

    def update_state(self, state: AnimState):
        if state != self.current_state:
            self.anim_idx = 0
            self.anim_timer = 0.0
            self.current_state = state

    def queue_next_animation(self, anim: AnimState):
        self.next_queued_animation = anim

    def update(self, dt: float):
        self.anim_timer += dt
        if self.anim_timer > self.anim_frame_length:
            self.anim_timer = 0
            self.anim_idx = (self.anim_idx + 1) % self.anim_len
            # If current animation is over, we take the queued animation
            if self.anim_idx == 0 and self.next_queued_animation != AnimState.NONE:
                self.current_state = self.next_queued_animation
                self.next_queued_animation = AnimState.NONE
