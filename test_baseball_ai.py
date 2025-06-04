"""
Baseball Manager Application
A comprehensive baseball team management system with player statistics and game tracking.
"""

from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class Player:
    """
    Represents a baseball player with comprehensive statistics.
    
    Attributes:
        player_id: Unique identifier for the player
        name: Full name of the player
        position: Primary playing position
        batting_average: Current season batting average
        home_runs: Number of home runs hit this season
        rbi: Runs batted in this season
        era: Earned run average (for pitchers only)
    """
    player_id: int
    name: str
    position: str
    batting_average: float
    home_runs: int
    rbi: int
    era: Optional[float] = None

class BaseballManager:
    """
    Baseball team management system for tracking players, games, and statistics.
    
    This class provides comprehensive functionality for managing a baseball team,
    including player management, statistics tracking, and game result recording.
    """
    
    def __init__(self, team_name: str):
        """
        Initialize the baseball manager with a team name.
        
        Args:
            team_name: The name of the baseball team to manage
        """
        self.team_name = team_name
        self.players: Dict[int, Player] = {}
        self.games: List[Dict[str, Any]] = []
        self.season_stats: Dict[str, Any] = {
            'wins': 0,
            'losses': 0,
            'total_runs': 0,
            'total_hits': 0
        }
        logger.info(f"Initialized baseball manager for team: {team_name}")
    
    def add_player(self, player: Player) -> bool:
        """
        Add a new player to the team roster.
        
        Args:
            player: Player object containing all player information
            
        Returns:
            True if player was successfully added, False if player already exists
            
        Raises:
            ValueError: If player data is invalid
        """
        try:
            if not isinstance(player, Player):
                raise ValueError("Invalid player object provided")
                
            if player.player_id in self.players:
                logger.warning(f"Player {player.name} already exists in roster")
                return False
                
            # Validate player statistics
            if not self._validate_player_stats(player):
                raise ValueError(f"Invalid statistics for player {player.name}")
                
            self.players[player.player_id] = player
            logger.info(f"Successfully added player {player.name} to {self.team_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding player {player.name}: {str(e)}")
            raise
    
    def _validate_player_stats(self, player: Player) -> bool:
        """
        Validate player statistics are within reasonable ranges.
        
        Args:
            player: Player object to validate
            
        Returns:
            True if all statistics are valid, False otherwise
        """
        if not (0.0 <= player.batting_average <= 1.0):
            return False
            
        if player.home_runs < 0 or player.rbi < 0:
            return False
            
        if player.era is not None and player.era < 0.0:
            return False
            
        return True
    
    def get_player_by_id(self, player_id: int) -> Optional[Player]:
        """
        Retrieve a player by their unique identifier.
        
        Args:
            player_id: The unique identifier of the player
            
        Returns:
            Player object if found, None otherwise
        """
        return self.players.get(player_id)
    
    def get_players_by_position(self, position: str) -> List[Player]:
        """
        Get all players who play a specific position.
        
        Args:
            position: The position to filter by (e.g., 'Pitcher', 'Catcher')
            
        Returns:
            List of players who play the specified position
        """
        return [
            player for player in self.players.values() 
            if player.position.lower() == position.lower()
        ]
    
    def calculate_team_batting_average(self) -> float:
        """
        Calculate the overall team batting average.
        
        Returns:
            Team batting average as a float between 0.0 and 1.0
        """
        if not self.players:
            return 0.0
            
        total_average = sum(player.batting_average for player in self.players.values())
        return total_average / len(self.players)
    
    def get_top_performers(self, stat: str, limit: int = 5) -> List[Player]:
        """
        Get the top performing players based on a specific statistic.
        
        Args:
            stat: The statistic to rank by ('batting_average', 'home_runs', 'rbi')
            limit: Maximum number of players to return
            
        Returns:
            List of top performing players sorted by the specified statistic
            
        Raises:
            ValueError: If the statistic name is not valid
        """
        valid_stats = ['batting_average', 'home_runs', 'rbi']
        
        if stat not in valid_stats:
            raise ValueError(f"Invalid statistic: {stat}. Must be one of {valid_stats}")
            
        sorted_players = sorted(
            self.players.values(),
            key=lambda p: getattr(p, stat),
            reverse=True
        )
        
        return sorted_players[:limit]
    
    def record_game_result(self, opponent: str, team_runs: int, opponent_runs: int, 
                          date: Optional[datetime] = None) -> None:
        """
        Record the result of a baseball game.
        
        Args:
            opponent: Name of the opposing team
            team_runs: Number of runs scored by this team
            opponent_runs: Number of runs scored by the opponent
            date: Date of the game (defaults to current date)
        """
        if date is None:
            date = datetime.now()
            
        game_result = {
            'opponent': opponent,
            'team_runs': team_runs,
            'opponent_runs': opponent_runs,
            'date': date.isoformat(),
            'result': 'win' if team_runs > opponent_runs else 'loss'
        }
        
        self.games.append(game_result)
        
        # Update season statistics
        if team_runs > opponent_runs:
            self.season_stats['wins'] += 1
        else:
            self.season_stats['losses'] += 1
            
        self.season_stats['total_runs'] += team_runs
        
        logger.info(f"Recorded game: {self.team_name} {team_runs} - {opponent} {opponent_runs}")
    
    def get_season_summary(self) -> Dict[str, Any]:
        """
        Generate a comprehensive season summary with key statistics.
        
        Returns:
            Dictionary containing season statistics and team performance metrics
        """
        total_games = self.season_stats['wins'] + self.season_stats['losses']
        win_percentage = (self.season_stats['wins'] / total_games) if total_games > 0 else 0.0
        
        return {
            'team_name': self.team_name,
            'total_games': total_games,
            'wins': self.season_stats['wins'],
            'losses': self.season_stats['losses'],
            'win_percentage': round(win_percentage, 3),
            'total_runs': self.season_stats['total_runs'],
            'average_runs_per_game': round(
                self.season_stats['total_runs'] / total_games, 2
            ) if total_games > 0 else 0.0,
            'roster_size': len(self.players),
            'team_batting_average': round(self.calculate_team_batting_average(), 3)
        }
    
    def export_roster_to_json(self, filename: str) -> bool:
        """
        Export the current roster to a JSON file.
        
        Args:
            filename: Name of the file to save the roster data
            
        Returns:
            True if export was successful, False otherwise
        """
        try:
            roster_data = {
                'team_name': self.team_name,
                'players': [
                    {
                        'player_id': player.player_id,
                        'name': player.name,
                        'position': player.position,
                        'batting_average': player.batting_average,
                        'home_runs': player.home_runs,
                        'rbi': player.rbi,
                        'era': player.era
                    }
                    for player in self.players.values()
                ]
            }
            
            with open(filename, 'w') as f:
                json.dump(roster_data, f, indent=2)
                
            logger.info(f"Successfully exported roster to {filename}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting roster: {str(e)}")
            return False

def main():
    """
    Demonstration of the Baseball Manager functionality.
    """
    # Create a new baseball team manager
    manager = BaseballManager("Springfield Isotopes")
    
    # Add some players to the roster
    players = [
        Player(1, "Homer Simpson", "Right Field", 0.284, 12, 45),
        Player(2, "Moe Szyslak", "Catcher", 0.312, 8, 38),
        Player(3, "Barney Gumble", "Pitcher", 0.201, 2, 15, 3.45),
        Player(4, "Carl Carlson", "First Base", 0.298, 15, 52),
        Player(5, "Lenny Leonard", "Second Base", 0.267, 7, 29)
    ]
    
    # Add players to the team
    for player in players:
        manager.add_player(player)
    
    # Record some game results
    manager.record_game_result("Shelbyville Sharks", 8, 5)
    manager.record_game_result("Capital City Goofballs", 4, 7)
    manager.record_game_result("Ogdenville Oregonians", 12, 3)
    
    # Display season summary
    summary = manager.get_season_summary()
    print(f"Season Summary for {summary['team_name']}:")
    print(f"Record: {summary['wins']}-{summary['losses']} ({summary['win_percentage']:.1%})")
    print(f"Team Batting Average: {summary['team_batting_average']}")
    
    # Show top performers
    top_hitters = manager.get_top_performers('batting_average', 3)
    print(f"\nTop 3 Hitters:")
    for i, player in enumerate(top_hitters, 1):
        print(f"{i}. {player.name}: {player.batting_average:.3f}")

if __name__ == "__main__":
    main()