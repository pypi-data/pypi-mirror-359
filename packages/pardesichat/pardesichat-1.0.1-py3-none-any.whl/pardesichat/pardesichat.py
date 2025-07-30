#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import socket
import threading
import sys
import ipaddress
import time
import random
import os

# --- Configuration ---
PORT = 13344
MODEL_PATH = 'gemma3n:e4b' # non-vision model
VISION_PATH = 'qwen2.5vl:3b' # Vision model

# --- Hangman Game Configuration & State ---
HANGMAN_STAGES = [
    # Stage 0: 0 wrong guesses
    """
       +---+
       |   |
           |
           |
           |
           |
    =========
    """,
    # Stage 1: 1 wrong guess
    """
       +---+
       |   |
       O   |
           |
           |
           |
    =========
    """,
    # Stage 2: 2 wrong guesses
    """
       +---+
       |   |
       O   |
       |   |
           |
           |
    =========
    """,
    # Stage 3: 3 wrong guesses
    """
       +---+
       |   |
       O   |
      /|   |
           |
           |
    =========
    """,
    # Stage 4: 4 wrong guesses
    """
       +---+
       |   |
       O   |
      /|\\  |
           |
           |
    =========
    """,
    # Stage 5: 5 wrong guesses
    """
       +---+
       |   |
       O   |
      /|\\  |
      /    |
           |
    =========
    """,
    # Stage 6: 6 wrong guesses (Game Over)
    """
       +---+
       |   |
       O   |
      /|\\  |
      / \\  |
           |
    =========
    """
]

# This dictionary will hold the state of the current hangman game
game_state = {
    'in_progress': False,
    'word': "",
    'word_progress': "",
    'wrong_guesses': 0,
    'guessed_letters': set(),
    'challenger': ""
}

# --- Stick Figure Fight Game Configuration & State ---
FIGHT_POSES = {
    'idle': "  O  \n /|\\ \n / \\ ",
    'punch': "  O-->>\n /|  \n / \\ ",
    'kick': "  O  \n /|\\ \n  / >",
    'block': "  O  \n /|\\ \n | | ",
    'hit': "   O \n  /|\\\n  / \\",
    'win': "  O__\n /|\\ \n / \\ ",
    'lose': "   X \n  /|\\\n  / \\",
    'special': " O<*>\n/|\\ \n/ \\ "
}

# This dictionary will hold the state of the current fight
fight_state = {
    'in_progress': False,
    'players': {},
    'player_names': [],
    'turn': "",
    'pending_challenge': {}
}


# --- Helper Functions ---

def clear_screen():
    """Clears the terminal screen for different operating systems."""
    if os.name == 'nt':
        _ = os.system('cls')
    else:
        _ = os.system('clear')

def reset_game_state():
    """Resets the hangman game state to its initial blank state."""
    global game_state
    game_state = {
        'in_progress': False, 'word': "", 'word_progress': "",
        'wrong_guesses': 0, 'guessed_letters': set(), 'challenger': ""
    }

def broadcast_game_state(clients, recipient_list=None):
    """Constructs and sends the current hangman state to players."""
    if not game_state['in_progress']:
        return
    word_display = " ".join(game_state['word_progress'])
    guessed_display = " ".join(sorted(list(game_state['guessed_letters'])))
    art = HANGMAN_STAGES[game_state['wrong_guesses']]
    message = f"""
{art}
Word: {word_display}
Guessed letters: [{guessed_display}]
"""
    
    if recipient_list:
        for conn in recipient_list:
            try:
                conn.send(message.encode('utf-8'))
            except:
                pass 
    else:
        broadcast(message.encode('utf-8'), None, clients)

def start_hangman_game(challenger_name, word, clients):
    """Initializes the game state for a new game of Hangman."""
    global game_state
    reset_game_state()
    game_state['in_progress'] = True
    game_state['word'] = word.upper()
    game_state['word_progress'] = ['_' if char.isalpha() else char for char in game_state['word']]
    game_state['challenger'] = challenger_name
    start_message = f"\n--- {challenger_name} has started a new game of Hangman! ---\nUse /guess <letter> to play. Use /quitgame to stop."
    broadcast(start_message.encode('utf-8'), None, clients)
    broadcast_game_state(clients)

def reset_fight_state():
    """Resets the fight game state to its initial blank state."""
    global fight_state
    fight_state = {
        'in_progress': False, 'players': {}, 'player_names': [],
        'turn': "", 'pending_challenge': {}
    }

def broadcast_fight_state(clients, p1_pose_key='idle', p2_pose_key='idle', action_text="", recipient_list=None):
    """Constructs and sends the current fight scene to players."""
    if not fight_state['in_progress']:
        return
    p1_name, p2_name = fight_state['player_names']
    p1_hp = fight_state['players'][p1_name]['hp']
    p2_hp = fight_state['players'][p2_name]['hp']
    p1_art_lines = FIGHT_POSES[p1_pose_key].split('\n')
    p2_art_lines = FIGHT_POSES[p2_pose_key].split('\n')
    scene = ""
    for i in range(len(p1_art_lines)):
        scene += f"{p1_art_lines[i]:<15}{p2_art_lines[i]:>15}\n"
    scene += f"{p1_name + ' (' + str(p1_hp) + ' HP)':<15}{p2_name + ' (' + str(p2_hp) + ' HP)':>15}\n"
    full_message = f"\n{scene}\n{action_text}\n"

    if recipient_list:
        for conn in recipient_list:
             try:
                conn.send(full_message.encode('utf-8'))
             except:
                pass
    else:
        broadcast(full_message.encode('utf-8'), None, clients)

def start_fight_game(clients):
    """Initializes the game state for a new fight."""
    global fight_state
    challenger = fight_state['pending_challenge']['challenger']
    opponent = fight_state['pending_challenge']['opponent']
    fight_state['in_progress'] = True
    fight_state['player_names'] = [challenger, opponent]
    fight_state['players'] = {
        challenger: {'hp': 100, 'special_used': False},
        opponent: {'hp': 100, 'special_used': False}
    }
    fight_state['turn'] = challenger
    fight_state['pending_challenge'] = {}
    start_message = f"\n--- {challenger} vs. {opponent}! FIGHT! ---"
    broadcast(start_message.encode('utf-8'), None, clients)
    broadcast_fight_state(clients, 'idle', 'idle', f"It is {challenger}'s turn. Choose your move: /punch, /kick, /block, /special")


def start_server(host_ip):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server_socket.bind(('0.0.0.0', PORT))
        server_socket.listen()
        print(f"[SERVER] Started. Listening for connections on port {PORT}")
        print(f"[SERVER] Other users can connect using this machine's IP: {host_ip}")
        clients = {}
        while True:
            client_conn, client_addr = server_socket.accept()
            print(f"[SERVER] New connection from {client_addr}")
            thread = threading.Thread(target=handle_client, args=(client_conn, clients))
            thread.daemon = True
            thread.start()
    except OSError as e:
        print(f"[SERVER] Error: {e}. Is port {PORT} already in use?")
    finally:
        server_socket.close()


def handle_client(connection, clients):
    """Receives messages, parses them for commands, and handles game logic."""
    username = ""
    try:
        username = connection.recv(1024).decode('utf-8')
        if not username or username in clients:
            error_msg = "[SYSTEM] Username is empty or already taken. Please reconnect with a different name."
            connection.send(error_msg.encode('utf-8'))
            time.sleep(1)
            connection.close()
            return
        
        clients[username] = connection
        
        connection.send("##CLEAR_SCREEN##".encode('utf-8'))
        time.sleep(0.1)
        welcome_art = f"""
   _____        _____  _____  ______  _____ _____ 
  |  __ \\ /\\   |  __ \\|  __ \\|  ____|/ ____|_   _|
  | |__) /  \\  | |__) | |  | | |__  | (___   | |  
  |  ___/ /\\ \\ |  _  /| |  | |  __|  \\___ \\  | |  
  | |  / ____ \\| | \\ \\| |__| | |____ ____) |_| |_ 
  |_| /_/    \\_\\_|  \\_\\_____/|______|_____/|_____|
                                                  
        --- 🔥 Welcome to Pardesi Chat, {username}! 🔥 ---
        
Type a message to chat, or try a command:
/whisper @<user> <message>
/hangman <word>
/fight @<user>
/ai <prompt>
"""
        connection.send(welcome_art.encode('utf-8'))
        broadcast(f"[SYSTEM] {username} has joined the chat.".encode('utf-8'), connection, clients)
        
        if game_state['in_progress']:
            broadcast_game_state(clients, recipient_list=[connection])
        elif fight_state['in_progress']:
            broadcast_fight_state(clients, 'idle', 'idle', f"A fight is in progress! It is {fight_state['turn']}'s turn.", recipient_list=[connection])

        while True:
            full_message = connection.recv(2048).decode('utf-8')
            if full_message:
                sender_username = full_message[full_message.find('<')+1:full_message.find('>')]
                message_content = full_message[full_message.find('>')+2:]

                if message_content.startswith('/'):
                    parts = message_content.split(' ', 2)
                    command = parts[0].lower()

                    if command in ['/whisper', '/msg']:
                        if len(parts) < 3:
                            connection.send("[SYSTEM] Usage: /whisper @<username> <message>".encode('utf-8'))
                        else:
                            recipient_name = parts[1][1:] if parts[1].startswith('@') else parts[1]
                            if recipient_name in clients:
                                private_message = parts[2]
                                clients[recipient_name].send(f"[Private from {sender_username}]: {private_message}".encode('utf-8'))
                                connection.send(f"[You whispered to {recipient_name}]: {private_message}".encode('utf-8'))
                            else:
                                connection.send(f"[SYSTEM] Error: User '{recipient_name}' not found.".encode('utf-8'))
                    
                    elif command == '/hangman':
                        if game_state['in_progress'] or fight_state['in_progress']:
                            connection.send("[GAME] A game is already in progress!".encode('utf-8'))
                        elif len(parts) < 2 or not parts[1].isalpha():
                            connection.send(f"[GAME] Usage: /hangman <word_to_guess> (e.g., /hangman python)".encode('utf-8')) 
                        else:
                            start_hangman_game(sender_username, parts[1], clients)
                    
                    elif command == '/guess':
                        if not game_state['in_progress']:
                            connection.send("[GAME] No hangman game is currently in progress.".encode('utf-8')) 
                        elif len(parts) < 2 or len(parts[1]) != 1 or not parts[1].isalpha():
                            connection.send(f"[GAME] Usage: /guess <single_letter>".encode('utf-8')) 
                        else:
                            
                            guess = parts[1].upper()
                            if guess in game_state['guessed_letters']:
                                broadcast(f"[GAME] '{guess}' has already been guessed.".encode('utf-8'), None, clients)
                            else:
                                
                                game_state['guessed_letters'].add(guess)
                                if guess in game_state['word']:
                                    for i, letter in enumerate(game_state['word']):
                                        if letter == guess: game_state['word_progress'][i] = guess
                                    broadcast(f"[GAME] {sender_username} guessed '{guess}' correctly!".encode('utf-8'), None, clients)
                                    if '_' not in game_state['word_progress']:
                                        broadcast_game_state(clients)
                                        broadcast(f"\n--- YOU WIN! The word was {game_state['word']}. Congratulations! ---\n".encode('utf-8'), None, clients)
                                        reset_game_state()
                                    else:
                                        broadcast_game_state(clients)
                                else:
                                    game_state['wrong_guesses'] += 1
                                    broadcast(f"[GAME] {sender_username} guessed '{guess}', which is WRONG!".encode('utf-8'), None, clients)
                                    if game_state['wrong_guesses'] >= len(HANGMAN_STAGES) - 1:
                                        broadcast_game_state(clients)
                                        broadcast(f"\n--- GAME OVER! The word was {game_state['word']}. ---\n".encode('utf-8'), None, clients)
                                        reset_game_state()
                                    else:
                                        broadcast_game_state(clients)

                    elif command == '/quitgame':
                        if game_state['in_progress'] and sender_username == game_state['challenger']:
                            broadcast(f"[GAME] {game_state['challenger']} has ended the game. The word was {game_state['word']}".encode('utf-8'), None, clients)
                            reset_game_state()
                        else:
                            connection.send("[GAME] There is no hangman game to quit or you didn't start it.".encode('utf-8')) 

                    elif command == '/fight':
                        if game_state['in_progress'] or fight_state['in_progress']:
                            connection.send("[GAME] A game is already in progress!".encode('utf-8')) 
                        elif len(parts) < 2 or not parts[1].startswith('@'):
                            connection.send("[GAME] Usage: /fight @<username>".encode('utf-8')) 
                        else:
                            opponent_name = parts[1][1:]
                            if opponent_name == sender_username:
                                connection.send("[GAME] You can't fight yourself!".encode('utf-8')) 
                            else:
                                fight_state['pending_challenge'] = {'challenger': sender_username, 'opponent': opponent_name}
                                challenge_msg = f"[GAME] {sender_username} has challenged {opponent_name} to a fight! {opponent_name}, type /accept to fight."
                                broadcast(challenge_msg.encode('utf-8'), None, clients)

                    elif command == '/accept':
                        if fight_state.get('pending_challenge', {}).get('opponent') == sender_username:
                            start_fight_game(clients)
                        else:
                            connection.send("[GAME] You have not been challenged to a fight.".encode('utf-8')) 

                    elif command in ['/punch', '/kick', '/block', '/special']:
                        if not fight_state['in_progress']:
                            connection.send("[GAME] No fight is in progress.".encode('utf-8')) 
                        elif sender_username != fight_state['turn']:
                            connection.send(f"[GAME] It's not your turn! It's {fight_state['turn']}'s turn.".encode('utf-8')) 
                        else:
                            
                            player1_name = sender_username
                            player2_name = fight_state['player_names'][1] if fight_state['player_names'][0] == player1_name else fight_state['player_names'][0]
                            action_text, p1_pose, p2_pose = "", 'idle', 'idle'
                            if command == '/punch':
                                p1_pose = 'punch'
                                if random.random() < 0.8:
                                    damage = 10
                                    fight_state['players'][player2_name]['hp'] -= damage
                                    action_text = f"{player1_name}'s punch connects for {damage} damage!"
                                    p2_pose = 'hit'
                                else:
                                    action_text = f"{player1_name}'s punch misses!"
                            elif command == '/kick':
                                p1_pose = 'kick'
                                if random.random() < 0.6:
                                    damage = 20
                                    fight_state['players'][player2_name]['hp'] -= damage
                                    action_text = f"{player1_name}'s kick lands for {damage} damage!"
                                    p2_pose = 'hit'
                                else:
                                    action_text = f"{player1_name}'s kick misses!"
                            elif command == '/special':
                                if fight_state['players'][player1_name]['special_used']:
                                    action_text = f"{player1_name} tried their special move, but has already used it!"
                                else:
                                    fight_state['players'][player1_name]['special_used'] = True
                                    p1_pose = 'special'
                                    action_text = f"{player1_name} attempts a high-risk special move!\n"
                                    if random.random() < 0.3:
                                        damage = int(fight_state['players'][player2_name]['hp'] * 0.5)
                                        fight_state['players'][player2_name]['hp'] -= damage
                                        action_text += f"IT CONNECTS! A devastating blow deals {damage} damage!"
                                        p2_pose = 'hit'
                                    else:
                                        action_text += f"But it fails, leaving them open!"
                            elif command == '/block':
                                p1_pose = 'block'
                                action_text = f"{player1_name} takes a defensive stance."
                            if fight_state['players'][player2_name]['hp'] <= 0:
                                p1_pose_for_win = 'win' if fight_state['player_names'][0] == player1_name else 'lose'
                                p2_pose_for_win = 'lose' if fight_state['player_names'][0] == player1_name else 'win'
                                broadcast_fight_state(clients, p1_pose_for_win, p2_pose_for_win, f"{action_text}\n--- {player1_name} WINS! ---")
                                reset_fight_state()
                            else:
                                fight_state['turn'] = player2_name
                                next_turn_text = f"It is {player2_name}'s turn. Choose your move: /punch, /kick, /block, /special"
                                if fight_state['player_names'][0] != player1_name:
                                    p1_pose, p2_pose = p2_pose, p1_pose
                                broadcast_fight_state(clients, p1_pose, p2_pose, f"{action_text}\n{next_turn_text}")
                    
                   # AI logic start --->

                    elif command == '/ai':
                        try:
                            import ollama
                            import requests
                            from PIL import Image
                            import io
                            from newspaper import Article

                            if len(parts) < 2:
                                connection.send("[SYSTEM] Usage: /ai <prompt> or /ai <url> <prompt>".encode('utf-8'))
                                return

                            first_arg = parts[1]

                            # LOGIC BRANCH 1: Handle Image URLs 
                            if first_arg.startswith('http') and first_arg.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                                image_url = first_arg
                                question = " ".join(parts[2:]) if len(parts) > 2 else "Describe this image in detail."

                                ai_thinking_msg = f"[AI Bot is analyzing the image and thinking about: \"{question}\"]"
                                broadcast(ai_thinking_msg.encode('utf-8'), None, clients)

                                response = requests.get(image_url, stream=True)
                                response.raise_for_status()
                                image_bytes = response.content

                                ollama_response = ollama.chat(
                                    model=VISION_PATH,
                                    messages=[{
                                        'role': 'user',
                                        'content': question,
                                        'images': [image_bytes]
                                    }]
                                )
                                response_text = ollama_response['message']['content']

                            # LOGIC BRANCH 2: Handle Article/Web Page URLs
                            elif first_arg.startswith('http'):
                                article_url = first_arg
                                question = " ".join(parts[2:]) if len(parts) > 2 else "Summarize the key points of this article."

                                ai_thinking_msg = f"[AI Bot is reading the article and thinking about: \"{question}\"]"
                                broadcast(ai_thinking_msg.encode('utf-8'), None, clients)

                                # Use newspaper3k to download and parse the article
                                article = Article(article_url)
                                article.download()
                                article.parse()
                                article_text = article.text

                                # Create a prompt that includes the article content
                                full_prompt = f"Based on the following article text, please answer this question: '{question}'\n\n--- ARTICLE TEXT ---\n{article_text}"

                                ollama_response = ollama.chat(
                                    model=MODEL_PATH,
                                    messages=[{'role': 'user', 'content': full_prompt}]
                                )
                                response_text = ollama_response['message']['content']

                            # LOGIC BRANCH 3: Handle Plain Text Questions 
                            else:
                                question = message_content[len(command)+1:]
                                ai_thinking_msg = f"[AI Bot is thinking about: \"{question}\"]"
                                broadcast(ai_thinking_msg.encode('utf-8'), None, clients)

                                ollama_response = ollama.chat(
                                    model=MODEL_PATH,
                                    messages=[{'role': 'user', 'content': question}]
                                )
                                response_text = ollama_response['message']['content']

                            ai_response_msg = f"[🤖 AI Bot]: {response_text}"
                            broadcast(ai_response_msg.encode('utf-8'), None, clients)

                        except ImportError:
                            broadcast("[AI] Required libraries for AI are not installed on the server.".encode('utf-8'), None, clients)
                        except Exception as e:
                            broadcast(f"[AI] Error contacting Ollama service. Is it running? Error: {e}".encode('utf-8'), None, clients)
                
                # AI logic end <----  

                else:
                    broadcast(full_message.encode('utf-8'), connection, clients)
            else:
                break 
    except Exception as e:
        print(f"[SERVER] Error in handle_client for {username}: {e}")
    finally:
        
        if username and username in clients:
            del clients[username]
            broadcast(f"[SYSTEM] {username} has left the chat.".encode('utf-8'), None, clients)
            if game_state['in_progress'] and username == game_state['challenger']:
                broadcast(f"[GAME] {game_state['challenger']} disconnected. The hangman game has ended.".encode('utf-8'), None, clients)
                reset_game_state()
            if fight_state['in_progress'] and username in fight_state['player_names']:
                 broadcast(f"[GAME] {username} disconnected. The fight is over.".encode('utf-8'), None, clients)
                 reset_fight_state()
        connection.close()


def broadcast(message, sender_connection, clients):
    """Broadcasts a message to all clients in the dictionary."""
    
    for conn in clients.values():
        if conn != sender_connection:
            try:
                conn.send(message)
            except:
                
                conn.close()


def start_client(host_ip):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((host_ip, PORT))
    except socket.error as e:
        print(f"Failed to connect to server: {e}")
        return

    receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
    receive_thread.daemon = True
    receive_thread.start()

    try:
        username = input("Enter your username: ")
        client_socket.send(username.encode('utf-8'))
        
        sys.stdout.write('> ')
        sys.stdout.flush()

        while True:
            message = input()
            if message.lower() == 'exit':
                break
            full_message = f"<{username}> {message}"
            client_socket.send(full_message.encode('utf-8'))
            
            sys.stdout.write('> ')
            sys.stdout.flush()
    except (EOFError, KeyboardInterrupt):
        print("\nLeaving chat.")
    finally:
        client_socket.close()
        print("\n--- You have left the chat. ---")

def receive_messages(sock):
    while True:
        try:
            message = sock.recv(2048).decode('utf-8')
            if message:
                if message == "##CLEAR_SCREEN##":
                    clear_screen()
                else:
                    sys.stdout.write('\r' + message + '\n')
                    sys.stdout.write('> ')
                    sys.stdout.flush()
            else:
                print("\r--- Connection to server has been lost. Press Enter to exit. ---")
                break
        except:
            print("\r--- Disconnected from server. Press Enter to exit. ---")
            break

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

def check_server(ip, port, open_ips):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(0.5)
    try:
        if sock.connect_ex((ip, port)) == 0:
            open_ips.append(ip)
    except socket.error:
        pass
    finally:
        sock.close()

def find_server():
    print(f"Searching for a server on port {PORT}...")
    local_ip = get_local_ip()
    if local_ip == '127.0.0.1' and len(sys.argv) < 2:
        print("Could not determine local network. Can't scan.")
        return None, '127.0.0.1'

    subnet = ipaddress.ip_network(f"{local_ip}/24", strict=False)
    threads = []
    found_servers = []
    
    for ip in subnet.hosts():
        ip = str(ip)
        thread = threading.Thread(target=check_server, args=(ip, PORT, found_servers))
        threads.append(thread)
        thread.start()
        
    for thread in threads:
        thread.join()

    if found_servers:
        return found_servers[0], local_ip
    else:
        return None, local_ip


# In[ ]:


# --- Main Execution Logic ---
def run_app():
    try:
        server_ip, my_ip = find_server()
    
        if server_ip:
            print(f"Server found at {server_ip}. Joining as client.")
            start_client(server_ip)
        else:
            print("No server found. Starting a new chat server...")
            
            server_thread = threading.Thread(target=start_server, args=(my_ip,))
            server_thread.daemon = True
            server_thread.start()
            
            time.sleep(1)
            
            print("Server started. Now starting your client...")
            start_client('127.0.0.1')
            
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        
    finally:
        print("\n--------------------")
        input("Press ENTER to exit...")


# In[ ]:


if __name__ == "__main__":
    run_app()

