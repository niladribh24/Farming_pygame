import json
import os
import pygame

class SaveManager:
    def __init__(self, filename='savegame.json'):
        self.filename = filename

    def save_game(self, player, soil_layer, learning_system, trees=None):
        """Save game state to JSON file"""
        
        # 1. Player Data
        player_data = {
            'money': player.money,
            'item_inventory': player.item_inventory,
            'seed_inventory': player.seed_inventory,
            'fertilizer_inventory': player.fertilizer_inventory,
            'water_reserve': player.water_reserve,
            'selected_tool_index': player.tool_index,
            'selected_seed_index': player.seed_index,
            # Skill levels
            'water_skill_level': player.water_skill_level,
            'speed_skill_level': player.speed_skill_level,
            'drip_irrigation_unlocked': player.drip_irrigation_unlocked,
            'drip_irrigation_count': player.drip_irrigation_count
        }

        # 2. Soil/Grid Data
        # We need to serialize the grid. 
        # For simplicity, we'll store active plants and modified tiles.
        # This might be large, but for a small farm it's fine.
        grid_data = []
        rows = len(soil_layer.grid)
        cols = len(soil_layer.grid[0])
        
        for y in range(rows):
            for x in range(cols):
                # Check for plant
                plant = None
                # Check sprite groups for plant at this position
                # This is a bit inefficient, but accurate.
                # Better: Check soil_layer.grid[y][x] flags if they exist, 
                # but valid plants are sprites.
                # Let's check collisions or just iterate sprites?
                # Iterating all plant sprites is better.
                pass

        # Optimized Soil saving:
        # Save soil health grid
        soil_health = soil_layer.soil_health_grid # 2D array
        
        # Save plants
        plants_data = []
        for plant in soil_layer.plant_sprites.sprites():
            # Get grid pos
            grid_x = plant.rect.centerx // 64 # TILE_SIZE
            grid_y = plant.rect.centery // 64
            
            plants_data.append({
                'x': grid_x,
                'y': grid_y,
                'type': plant.plant_type,
                'age': plant.age,
                'harvestable': plant.harvestable,
                'unwatered_days': plant.unwatered_days,
                'fertilized_days': plant.fertilized_days,
                'total_grow_days': plant.total_grow_days
            })

        # Save drip irrigation setups
        drip_data = []
        for drip in soil_layer.drip_irrigation_sprites.sprites():
            drip_data.append({
                'x': drip.grid_x,
                'y': drip.grid_y
            })

        soil_data = {
            'soil_health': soil_health,
            'grid': soil_layer.grid,
            'water_count': soil_layer.water_count_grid,
            'last_crop': soil_layer.last_crop_grid,
            'plants': plants_data,
            'drip_setups': drip_data
        }

        # 3. Learning System Data
        learning_data = {
            'day': learning_system.current_day,
            'score': learning_system.total_score,
            'daily_actions': learning_system.daily_actions,
            'achievements': list(learning_system.achievements), # Set to list
            'skills': self._serialize_skills(learning_system.skill_tree)
        }

        # 4. Tree Data
        tree_data = []
        if trees:
             for tree in trees.sprites():
                 tree_data.append({
                     'x': tree.rect.x,
                     'y': tree.rect.y,
                     'alive': tree.alive,
                     'timer': tree.respawn_timer
                 })

        # Master Save Data
        save_data = {
            'player': player_data,
            'soil': soil_data,
            'learning': learning_data,
            'trees': tree_data
        }

        with open(self.filename, 'w') as f:
            json.dump(save_data, f, indent=4)
        
        print("Game Saved!")

    def load_game(self, player, soil_layer, learning_system, trees=None):
        """Load game state from JSON file"""
        if not os.path.exists(self.filename):
            print("No save file found.")
            return False

        try:
            with open(self.filename, 'r') as f:
                data = json.load(f)
            
            # 1. Load Player
            p_data = data.get('player', {})
            player.money = p_data.get('money', 200)
            player.item_inventory = p_data.get('item_inventory', player.item_inventory)
            player.seed_inventory = p_data.get('seed_inventory', player.seed_inventory)
            player.fertilizer_inventory = p_data.get('fertilizer_inventory', player.fertilizer_inventory)
            player.water_reserve = p_data.get('water_reserve', 0)
            
            # Load skill levels
            player.water_skill_level = p_data.get('water_skill_level', 0)
            player.speed_skill_level = p_data.get('speed_skill_level', 0)
            player.drip_irrigation_unlocked = p_data.get('drip_irrigation_unlocked', False)
            player.drip_irrigation_count = p_data.get('drip_irrigation_count', 0)
            player._apply_skill_effects()  # Apply skill effects after loading

            # 2. Load Learning System
            l_data = data.get('learning', {})
            learning_system.current_day = l_data.get('day', 0)
            learning_system.total_score = l_data.get('score', 0)
            learning_system.daily_actions = l_data.get('daily_actions', [])
            if 'achievements' in l_data:
                learning_system.achievements = set(l_data['achievements'])
            # Skills loading would be complex, mostly just need to mark unlocked ones
            # For now, let's trust the achievement/score based unlocks or save skill status explicitly?
            # Implemented simple skill load if structure permits.

            # 3. Load Soil/Plants
            s_data = data.get('soil', {})
            
            # Restore soil health
            saved_health = s_data.get('soil_health')
            if saved_health:
                soil_layer.soil_health_grid = saved_health
            
            # Restore Grid and Tiles
            if 'grid' in s_data:
                soil_layer.grid = s_data['grid']
                soil_layer.create_soil_tiles()
            
            if 'water_count' in s_data:
                soil_layer.water_count_grid = s_data['water_count']
            if 'last_crop' in s_data:
                soil_layer.last_crop_grid = s_data['last_crop']
            
            # Clear existing plants
            for sprite in soil_layer.plant_sprites.sprites():
                sprite.kill()
            
            # Restore plants
            if 'plants' in s_data:
                for p_info in s_data['plants']:
                    x, y = p_info['x'], p_info['y']
                    # Use soil_layer to spawn plant
                    # We need to manually recreate the plant object
                    
                    # We can use soil_layer.grid[y][x] to find the soil tile?
                    # No, soil_layer doesn't keep easy ref to tiles in grid structure for spawning usually?
                    # wait, soil_layer.grid "F" means farmland.
                    
                    # Let's call a method on soil_layer or manually spawn
                    # The standard create_plant logic:
                    # self.plant_sprites.add(Plant(plant_type, groups, tile, check_watered))
                    
                    # We need the 'soil' tile object at x,y.
                    # soil_layer.soil_sprites has them. 
                    # Finding exact sprite by grid pos is annoying unless we map it.
                    
                    # Better: Iterate soil sprites and match position.
                    target_pixel_x = x * 64
                    target_pixel_y = y * 64
                    
                    found_tile = None
                    for tile in soil_layer.soil_sprites.sprites():
                        if tile.rect.x == target_pixel_x and tile.rect.y == target_pixel_y:
                            found_tile = tile
                            break
                    
                    if found_tile:
                        # Recreate plant with all data
                        plant = soil_layer._force_plant(
                            found_tile, p_info['type'], p_info['age'], 
                            p_info['harvestable'], p_info.get('unwatered_days', 0),
                            p_info.get('fertilized_days', 0), p_info.get('total_grow_days', 0)
                        )
            
            # Load drip irrigation setups
            if 'drip_setups' in s_data:
                from soil import DripIrrigationSetup
                for drip_info in s_data['drip_setups']:
                    x, y = drip_info['x'], drip_info['y']
                    pixel_x = x * 64
                    pixel_y = y * 64
                    DripIrrigationSetup((pixel_x, pixel_y), [soil_layer.all_sprites, soil_layer.drip_irrigation_sprites])
            
            print("Game Loaded!")
            
            # 4. Load Trees
            t_data = data.get('trees', [])
            if trees and t_data:
                # Map loaded count to current trees by position
                # This assumes trees don't move.
                for t_info in t_data:
                    tx, ty = t_info.get('x'), t_info.get('y')
                    talive = t_info.get('alive', True)
                    ttimer = t_info.get('timer', 0)
                    
                    # Find matching tree
                    for tree in trees.sprites():
                        if tree.rect.x == tx and tree.rect.y == ty:
                             tree.alive = talive
                             tree.respawn_timer = ttimer
                             
                             # Update visual if dead
                             if not tree.alive:
                                 tree.image = tree.stump_surf
                                 tree.rect = tree.image.get_rect(midbottom = tree.rect.midbottom)
                                 tree.hitbox = tree.rect.copy().inflate(-10,-tree.rect.height * 0.6)
                                 
                                 # Kill apples if dead
                                 for apple in tree.apple_sprites.sprites():
                                     apple.kill()
                             break

            return True

        except Exception as e:
            print(f"Error loading save: {e}")
            return False

    def _serialize_skills(self, skill_tree):
        # Todo: serialize skill states if needed
        return {}
