# Zeppelin Betting Game

## Overview

This is a Flask-based real-time betting game called "Zeppelin" that integrates with Kick streaming platform. Players can place bets via chat commands and watch live game results. The application features a web interface for gameplay visualization and an admin panel for monitoring users and game statistics.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Backend Architecture
- **Framework**: Flask with Socket.IO for real-time communication
- **Language**: Python 3.x
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Real-time Communication**: WebSocket connections via Socket.IO
- **Data Storage**: PostgreSQL database with persistent storage
- **API Integration**: Mock Kick API implementation (ready for real integration)

### Frontend Architecture
- **Template Engine**: Jinja2 (Flask's default)
- **Styling**: Bootstrap 5 with dark theme
- **JavaScript**: Vanilla JS with Socket.IO client
- **Real-time Updates**: WebSocket-based live game feed

### File Structure
```
├── app.py              # Main Flask application
├── main.py             # Application entry point  
├── models.py           # PostgreSQL database models
├── database_manager.py # Database operations and user management
├── game_logic.py       # Core game mechanics
├── kick_api.py         # Kick platform integration (mock)
├── templates/          # HTML templates
├── static/             # CSS and JavaScript assets
```

## Key Components

### Game Logic (`game_logic.py`)
- **Win Rate**: 35% configured win probability
- **Multiplier Range**: 1.0x to 50.0x
- **Betting System**: Players set target multipliers and bet amounts
- **Random Number Generation**: Determines actual multipliers for game outcomes

### Database Management (`database_manager.py`)
- **Registration**: Automatic user registration based on follower count
- **Balance System**: Point-based economy with starting balances
- **Subscriber Rewards**: 100+ subscribers get 1000 starting points, others get 0
- **Data Persistence**: PostgreSQL database with SQLAlchemy ORM
- **Game History**: Complete game result tracking and statistics

### Kick API Integration (`kick_api.py`)
- **Mock Implementation**: Currently uses mock data for development
- **Channel Monitoring**: Tracks follower count and live status
- **Chat Integration**: Framework for listening to chat commands
- **Real API Ready**: Structure prepared for actual Kick API integration

### Real-time Communication
- **Socket.IO Events**: 
  - `user_registered`: New user notifications
  - `game_result`: Live game outcomes
  - `connect/disconnect`: Connection status updates
- **Live Feed**: Real-time display of game results and user activities

## Data Flow

1. **User Registration**: 
   - User triggers chat command → Kick API checks follower count → User registered with appropriate balance
   
2. **Game Play**:
   - Chat command parsed → Bet validation → Game logic execution → Result broadcast via Socket.IO
   
3. **Balance Management**:
   - Automatic deduction on bets → Winnings calculation and addition → Persistent storage update

## External Dependencies

### Production Dependencies
- **Flask**: Web framework
- **Flask-SocketIO**: Real-time communication
- **Flask-SQLAlchemy**: Database ORM
- **PostgreSQL**: Primary database
- **psycopg2-binary**: PostgreSQL adapter
- **Bootstrap 5**: Frontend styling
- **Socket.IO**: Client-side real-time communication

### Development Setup
- **Mock Kick API**: Simulates streaming platform integration
- **PostgreSQL Database**: Full database persistence
- **Environment Variables**: Configuration for API keys and secrets
- **Migration Support**: JSON to PostgreSQL data migration

### Future Integration Points
- **Kick API**: Real streaming platform integration
- **Authentication**: User session management
- **Payment Integration**: Real money transactions (if needed)
- **Advanced Analytics**: Detailed game statistics and reporting

## Deployment Strategy

### Current Setup
- **Development Server**: Flask development server with Socket.IO
- **Static Assets**: Served directly by Flask
- **Data Storage**: PostgreSQL database with full persistence
- **Configuration**: Environment variables for sensitive data

### Production Considerations
- **Database**: PostgreSQL fully integrated and operational
- **Session Management**: Redis for Socket.IO scaling
- **Load Balancing**: Multiple Flask instances support
- **Static Files**: CDN integration for better performance
- **Monitoring**: Logging framework already implemented

### Environment Variables
- `SESSION_SECRET`: Flask session security
- `KICK_API_KEY`: Kick platform authentication
- `KICK_CHANNEL_ID`: Target streaming channel

The application is designed with scalability in mind, using modular components that can be easily upgraded from the current MVP implementation to a production-ready system with proper database integration and real API connections.