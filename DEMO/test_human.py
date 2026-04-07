import pygame
from prairie_king.envs.prairie_king_env import PrairieKingEnv

def test_drawing():
    env = PrairieKingEnv(render_mode="human")
    obs, _ = env.reset()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()

        # ====================== MOVEMENT ======================
        move_action = 0                     # default = no movement

        if keys[pygame.K_w] or keys[pygame.K_UP]:
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                move_action = 5   # up-left
            elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                move_action = 6   # up-right
            else:
                move_action = 1   # up
        elif keys[pygame.K_s] or keys[pygame.K_DOWN]:
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                move_action = 7   # down-left
            elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                move_action = 8   # down-right
            else:
                move_action = 2   # down
        elif keys[pygame.K_a] or keys[pygame.K_LEFT]:
            move_action = 3       # left
        elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            move_action = 4       # right

        # ====================== SHOOTING ======================
        shoot_action = 0                    # default = no shoot

        if keys[pygame.K_SPACE]:
            shoot_action = 1                # shoot up
        elif keys[pygame.K_j]:
            shoot_action = 2                # shoot down
        elif keys[pygame.K_k]:
            shoot_action = 3                # shoot left
        elif keys[pygame.K_l]:
            shoot_action = 4                # shoot right
        elif keys[pygame.K_u]:
            shoot_action = 5                # shoot up-left
        elif keys[pygame.K_i]:
            shoot_action = 6                # shoot up-right
        elif keys[pygame.K_n]:
            shoot_action = 7                # shoot down-left
        elif keys[pygame.K_m]:
            shoot_action = 8                # shoot down-right

        # Combine into one action for the environment
        action = [move_action, shoot_action]

        # Step the environment
        obs, reward, terminated, truncated, info = env.step(action)

        if terminated:
            print("Game Over - Player died!")
            obs, _ = env.reset()

    env.close()


if __name__ == "__main__":
    test_drawing()