# Main game entry point moved to end of file to ensure all functions are defined
intro_sequence()

while True:
    mode = main_menu()
    if mode == 'single':
        single_player_menu()
        player_name = get_name()
        play_music(music_Game)
        # Place your single player game loop here (the code that was previously under 'if mode == "single":')
        # ...existing code...
    elif mode == 'multi':
        multiplayer_game_loop()
    else:
        break
