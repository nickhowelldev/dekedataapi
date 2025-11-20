from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from decimal import Decimal


class SeasonStatsDetail(BaseModel):
    gp: int = 0
    g: int = 0
    a: int = 0
    pts: int = 0
    pim: Optional[int] = None
    plus_minus: Optional[int] = None
    sog: Optional[int] = None
    hits: Optional[int] = None
    blocks: Optional[int] = None
    pp_g: Optional[int] = None
    sh_g: Optional[int] = None
    model_config = ConfigDict(from_attributes=True)


class GoalieSeasonStatsDetail(BaseModel):
    gp: int = 0
    gs: Optional[int] = None
    w: Optional[int] = None
    l: Optional[int] = None
    otl: Optional[int] = None
    so: Optional[int] = None
    ga: Optional[int] = None
    sa: Optional[int] = None
    sv: Optional[int] = None
    toi_min: Optional[int] = None
    gaa: Optional[Decimal] = None
    sv_pct: Optional[Decimal] = None
    model_config = ConfigDict(from_attributes=True)


class PlayerSeasonResponse(BaseModel):
    season: str
    league: str
    league_code: str
    team: Optional[str] = None
    team_code: Optional[str] = None
    split: str = "Regular"
    age: Optional[int] = None
    level: Optional[str] = None
    competition_strength: Optional[Decimal] = None
    stats: Optional[SeasonStatsDetail] = None
    goalie_stats: Optional[GoalieSeasonStatsDetail] = None
    model_config = ConfigDict(from_attributes=True)


class PlayerSeasonsResponse(BaseModel):
    seasons: List[PlayerSeasonResponse]
    stats: Optional[SeasonStatsDetail] = None
    goalie_stats: Optional[GoalieSeasonStatsDetail] = None


class YouthScoreDetail(BaseModel):
    age: int
    season: Optional[str] = None
    overall: Decimal
    prospect: Optional[Decimal] = None
    skating: Optional[Decimal] = None
    shot: Optional[Decimal] = None
    iq: Optional[Decimal] = None
    compete: Optional[Decimal] = None
    physical: Optional[Decimal] = None
    projection_note: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class PlayerYouthScoresResponse(BaseModel):
    youth_scores: List[YouthScoreDetail]


class DraftProbabilityDetail(BaseModel):
    draft_league: str
    season: Optional[str] = None
    probability: Decimal
    round_estimate: Optional[int] = None
    team_hints: Optional[List[str]] = None
    model_config = ConfigDict(from_attributes=True)


class PlayerDraftResponse(BaseModel):
    drafts: List[DraftProbabilityDetail]


class SeasonProgressSnapshot(BaseModel):
    date: str
    gp: int = 0
    g: int = 0
    a: int = 0
    pts: int = 0
    pim: Optional[int] = None
    plus_minus: Optional[int] = None
    sog: Optional[int] = None
    hits: Optional[int] = None
    blocks: Optional[int] = None
    pp_g: Optional[int] = None
    sh_g: Optional[int] = None


class GoalieSeasonProgressSnapshot(BaseModel):
    date: str
    gp: int = 0
    gs: Optional[int] = None
    w: Optional[int] = None
    l: Optional[int] = None
    otl: Optional[int] = None
    so: Optional[int] = None
    ga: Optional[int] = None
    sa: Optional[int] = None
    sv: Optional[int] = None
    toi_min: Optional[int] = None
    gaa: Optional[Decimal] = None
    sv_pct: Optional[Decimal] = None


class PlayerSeasonProgressResponse(BaseModel):
    snapshots: List[SeasonProgressSnapshot] = []
    goalie_snapshots: List[GoalieSeasonProgressSnapshot] = []
    message: Optional[str] = None


class PlayerDetails(BaseModel):
    player_id: str
    name: str
    position: str
    birth_year: Optional[int] = None
    shoots: Optional[str] = None
    height: Optional[Decimal] = None
    weight: Optional[Decimal] = None
    photo_url: Optional[str] = None


class PlayerProfileResponse(BaseModel):
    details: PlayerDetails
    seasons: List[PlayerSeasonResponse] = []
    stats: Optional[SeasonStatsDetail] = None
    goalie_stats: Optional[GoalieSeasonStatsDetail] = None
    youth_scores: List[YouthScoreDetail] = []
    snapshots: Optional[PlayerSeasonProgressResponse] = None
    probabilities: List[DraftProbabilityDetail] = []
