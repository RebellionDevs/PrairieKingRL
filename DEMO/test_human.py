import pygame
from prairie_king.envs.prairie_king_env import PrairieKingEnv

def test_drawing():
    env = PrairieKingEnv(render_mode="human")
    
    obs, _ = env.reset()        # This calls world.reset() → create_map()
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        # Let the player stand still (action 0 = noop)
        obs, reward, terminated, truncated, info = env.step(0)
        
        # Optional: move around with keyboard to test collision + drawing
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            env.step(1)
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            env.step(2)
        elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
            env.step(3)
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            env.step(4)
        
        env.render()                # This draws visible_sprites
        pygame.display.set_caption(f"Prairie King Drawing Test | FPS: {env.clock.get_fps():.1f}")
    
    env.close()

if __name__ == "__main__":
    test_drawing()