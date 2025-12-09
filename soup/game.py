import json
import os
import random
from typing import Dict, Union

from rich.console import Console
from rich.text import Text

from soup.agents import answer_agent, judge_agent
from soup.agents.dep import SoupState
from soup.config import BASE_DIR, logger
from soup.comm.msg import GameMsg


class SoupFlow:
    """Main game flow controller for Lateral Thinking Puzzles (海龟汤)"""
    
    def __init__(self):
        # AI agents
        self.judge_agent = judge_agent
        self.answer_agent = answer_agent
        
        # Game state
        self.ai_running = False
        self.chat_history = []
        self.game_state = {
            "game_id": 0,
            "running": False,
            "current_soup": None,
        }
        
        # Load puzzles
        self.soups = self._load_soups()
        
        # Console for CLI output
        self.console = Console()
    
    def _load_soups(self) -> list:
        """Load soup puzzles from JSON file"""
        soup_path = os.path.join(BASE_DIR, "soups.json")
        try:
            with open(soup_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"Soups file not found: {soup_path}")
            return []
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in soups file: {e}")
            return []
    
    def get_random_soup(self) -> Dict:
        """Select a random puzzle"""
        if not self.soups:
            logger.error("No soups available!")
            return {"question": "Error: No puzzles loaded", "answer": "N/A"}
        return random.choice(self.soups)
    
    def add_message(self, speaker: str, content: str) -> None:
        """Add a message to chat history"""
        self.chat_history.append({
            'sayer': speaker,
            'content': content
        })
    
    def start_new_game(self) -> None:
        """Start a new game with a random puzzle"""
        self.end_game()
        
        self.game_state["game_id"] += 1
        self.game_state["running"] = True
        self.game_state["current_soup"] = self.get_random_soup()
        
        question = self.game_state['current_soup']['question']
        msg = f"新游戏开始了: {question}"
        
        self.add_message('主持人', msg)
        logger.info(f"Game #{self.game_state['game_id']} started: {question}")
    
    def end_game(self) -> None:
        """End the current game and reset state"""
        if self.game_state["running"]:
            logger.info(f"Game #{self.game_state['game_id']} ended")
        
        self.game_state["running"] = False
        self.game_state["current_soup"] = None
        self.chat_history = []
    
    def _extract_input(self, user_input: Union[str, Dict]) -> tuple[str, str]:
        """Extract content and speaker from input"""
        if isinstance(user_input, dict):
            content = user_input.get('content', '').strip()
            speaker = user_input.get('speaker', '匿名玩家')
        else:
            content = str(user_input).strip()
            speaker = '匿名玩家'
        
        return content, speaker
    
    def _create_response(self, msg: str, speaker: str = '主持人') -> GameMsg:
        """Create a standardized response message"""
        response = GameMsg()
        response["msg"] = msg
        response["speaker"] = speaker
        return response
    
    def handle_ask(self, user_input: Union[str, Dict]) -> GameMsg:
        """Handle a yes/no question from player"""
        content, speaker = self._extract_input(user_input)
        
        # Check game state
        if not self.game_state["running"]:
            return self._create_response("游戏未运行，请先开始新游戏")
        
        # Set AI running flag
        self.ai_running = True
        
        try:
            # Add user question to chat
            self.add_message(speaker, content)
            
            # Get AI judgment
            judge_result = self.judge_agent.run_sync(
                content,
                deps=SoupState(**self.game_state)
            )
            
            # Format response
            judgment = judge_result.output.result
            reasoning = judge_result.output.reasoning
            
            response_msg = f"判断：{judgment}"
            self.add_message('主持人', response_msg)
            
            # Log detailed reasoning (CLI only)
            full_msg = f"{response_msg}\n依据：{reasoning}"
            self.console.print(Text(full_msg, style="bold blue"))
            logger.info(f"Question: {content} -> {judgment}")
            
            return self._create_response(response_msg)
            
        except Exception as e:
            logger.error(f"Error in handle_ask: {e}")
            return self._create_response("处理问题时出错，请重试")
        
        finally:
            self.ai_running = False
    
    def handle_answer(self, user_input: Union[str, Dict]) -> GameMsg:
        """Handle a solution attempt from player"""
        content, speaker = self._extract_input(user_input)
        
        # Check game state
        if not self.game_state["running"]:
            return self._create_response("游戏未运行，请先开始新游戏")
        
        # Set AI running flag
        self.ai_running = True
        
        try:
            # Add user answer to chat
            self.add_message(speaker, content)
            
            # Get AI evaluation
            answer_result = self.answer_agent.run_sync(
                content,
                deps=SoupState(**self.game_state)
            )
            
            # Check if correct
            if answer_result.output.result == "正确":
                correct_answer = self.game_state['current_soup']['answer']
                response_msg = f"🎉 恭喜你，猜对了！汤底是：{correct_answer}"
                
                self.console.print(Text(response_msg, style="bold green"))
                logger.info(f"Correct answer by {speaker}: {content}")
                
                self.add_message('主持人', response_msg)
                # self.end_game()
                
            else:
                reasoning = answer_result.output.reasoning
                response_msg = "很遗憾，回答错误"
                
                full_msg = f"{response_msg}\n依据：{reasoning}"
                self.console.print(Text(full_msg, style="bold yellow"))
                logger.info(f"Wrong answer by {speaker}: {content}")
                
                self.add_message('主持人', response_msg)
            
            return self._create_response(response_msg)
            
        except Exception as e:
            logger.error(f"Error in handle_answer: {e}")
            return self._create_response("处理答案时出错，请重试")
        
        finally:
            self.ai_running = False
    
    # CLI interface
    def run(self, user_input: str) -> None:
        """Handle CLI input (for command-line interface)"""
        cmd = user_input.strip().lower()
        
        # Start new game
        if cmd == "start":
            self.start_new_game()
            question = self.game_state['current_soup']['question']
            self.console.print(Text(f"汤面：{question}", style="bold green"))
            return
        
        # Quit game
        if cmd == "quit":
            self.end_game()
            self.console.print(Text("游戏结束", style="bold red"))
            return
        
        # Check if game is running
        if not self.game_state["running"]:
            self.console.print(
                Text("游戏未开始。请输入 'start' 开始新游戏", style="bold red")
            )
            return
        
        # Handle ask command
        if cmd.startswith("ask"):
            question = user_input[3:].strip()
            if question:
                self.handle_ask(question)
            else:
                self.console.print(Text("请在 'ask' 后输入问题", style="bold red"))
            return
        
        # Handle answer command
        if cmd.startswith("ans"):
            answer = user_input[3:].strip()
            if answer:
                self.handle_answer(answer)
            else:
                self.console.print(Text("请在 'ans' 后输入答案", style="bold red"))
            return
        
        # Unknown command
        self.console.print(Text("无法识别的输入。使用 'ask <问题>' 或 'ans <答案>'", style="bold red"))