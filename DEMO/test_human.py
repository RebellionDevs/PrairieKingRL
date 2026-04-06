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
        
        obs, reward, terminated, truncated, info = env.step([0, 0])
        
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            env.world.shoot((0, -1))
        elif keys[pygame.K_s]:
            env.world.shoot((0, 1))
        elif keys[pygame.K_a]:
            env.world.shoot((-1, 0))
        elif keys[pygame.K_d]:
            env.world.shoot((1, 0))
        elif keys[pygame.K_z]:
            env.world.shoot((1, 1))
        
        env.render()
        pygame.display.set_caption(f"Prairie King Drawing Test | FPS: {env.clock.get_fps():.1f}")
    
    env.close()

if __name__ == "__main__":
    test_drawing()