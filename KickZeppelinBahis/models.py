import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime
from typing import Dict, Any, Optional


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)


class User(db.Model):
    """Kullanıcı modeli"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    balance = db.Column(db.Float, default=0.0, nullable=False)
    total_bets = db.Column(db.Float, default=0.0, nullable=False)
    total_winnings = db.Column(db.Float, default=0.0, nullable=False)
    games_played = db.Column(db.Integer, default=0, nullable=False)
    registration_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    last_activity = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    subscriber_count_at_registration = db.Column(db.Integer, default=0, nullable=False)
    
    # İlişkiler
    game_results = db.relationship('GameResult', backref='player', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self) -> Dict[str, Any]:
        """Kullanıcı verilerini dict olarak döndür"""
        return {
            'id': self.id,
            'username': self.username,
            'balance': self.balance,
            'total_bets': self.total_bets,
            'total_winnings': self.total_winnings,
            'games_played': self.games_played,
            'registration_date': self.registration_date.isoformat(),
            'last_activity': self.last_activity.isoformat(),
            'subscriber_count_at_registration': self.subscriber_count_at_registration
        }
    
    def update_activity(self):
        """Kullanıcı aktivitesini güncelle"""
        self.last_activity = datetime.utcnow()
    
    def __repr__(self):
        return f'<User {self.username}>'


class GameResult(db.Model):
    """Oyun sonuçları modeli"""
    __tablename__ = 'game_results'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    bet_amount = db.Column(db.Float, nullable=False)
    target_multiplier = db.Column(db.Float, nullable=False)
    actual_multiplier = db.Column(db.Float, nullable=False)
    won = db.Column(db.Boolean, nullable=False)
    winnings = db.Column(db.Float, default=0.0, nullable=False)
    game_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def to_dict(self) -> Dict[str, Any]:
        """Oyun sonucunu dict olarak döndür"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'username': self.player.username if self.player else None,
            'bet_amount': self.bet_amount,
            'target_multiplier': self.target_multiplier,
            'actual_multiplier': self.actual_multiplier,
            'won': self.won,
            'winnings': self.winnings,
            'game_date': self.game_date.isoformat()
        }
    
    def __repr__(self):
        return f'<GameResult {self.player.username}: {self.bet_amount} -> {self.winnings}>'


class GameStats(db.Model):
    """Oyun istatistikleri modeli"""
    __tablename__ = 'game_stats'
    
    id = db.Column(db.Integer, primary_key=True)
    stat_date = db.Column(db.Date, default=datetime.utcnow().date, nullable=False, unique=True, index=True)
    total_games = db.Column(db.Integer, default=0, nullable=False)
    total_bets = db.Column(db.Float, default=0.0, nullable=False)
    total_winnings = db.Column(db.Float, default=0.0, nullable=False)
    active_users = db.Column(db.Integer, default=0, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """İstatistikleri dict olarak döndür"""
        return {
            'stat_date': self.stat_date.isoformat(),
            'total_games': self.total_games,
            'total_bets': self.total_bets,
            'total_winnings': self.total_winnings,
            'active_users': self.active_users,
            'updated_at': self.updated_at.isoformat()
        }
    
    def __repr__(self):
        return f'<GameStats {self.stat_date}: {self.total_games} games>'


def get_or_create_daily_stats() -> GameStats:
    """Günlük istatistikleri getir veya oluştur"""
    today = datetime.utcnow().date()
    stats = GameStats.query.filter_by(stat_date=today).first()
    
    if not stats:
        stats = GameStats(stat_date=today)
        db.session.add(stats)
        db.session.commit()
    
    return stats