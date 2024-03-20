use Groep4_DEP1;
CREATE TABLE DimensionTeam (
    teamId INT PRIMARY KEY,
    TeamName VARCHAR(255),
    StamNumber INT
);


CREATE TABLE FactTableMatch (
    MatchId INT PRIMARY KEY,
    HomeTeam INT,
    AwayTeam INT,
    MatchDay DATE,
    HomeTeamScore INT,
    AwayTeamScore INT,
    Result VARCHAR(1),
    GoalsScored INT,
    Playday INT,
    SeasonYear INT,
    StartingHour TIME,
    EndingHour TIME,
    FOREIGN KEY (HomeTeam) REFERENCES DimensionTeam(teamId),
    FOREIGN KEY (AwayTeam) REFERENCES DimensionTeam(teamId)
);

CREATE TABLE FactTableBet (
    BettingId INT PRIMARY KEY,
    HomeTeam INT,
    AwayTeam INT,
    MatchId INT,
    MatchDay DATE,
    OddsHome DECIMAL(5,2),
    OddsAway DECIMAL(5,2),
    OddsDraw DECIMAL(5,2),
    OddsUnderGoals DECIMAL(5,2),
    OddsOverGoals DECIMAL(5,2),
    FOREIGN KEY (HomeTeam) REFERENCES DimensionTeam(teamId),
    FOREIGN KEY (AwayTeam) REFERENCES DimensionTeam(teamId),
    FOREIGN KEY (MatchId) REFERENCES FactTableMatch(MatchId)
);


CREATE TABLE DimensionStandings (
    StandingsDayId INT PRIMARY KEY,
    StandingsPlayday INT,
    StandingsYear INT,
    ClubID INT,
    Ranking INT,
    Points INT,
    Wins INT,
    Ties INT,
    Losses INT,
    GoalDifference INT,
    FOREIGN KEY (ClubID) REFERENCES DimensionTeam(teamId)
);

CREATE TABLE DimensionGoal (
    GoalId INT PRIMARY KEY,
    MatchId INT,
    GoalTimeRelative INT,
    TeamScored INT,
    HomeScore INT,
    AwayScore INT,
    AbsoluteTime TIME,
    FOREIGN KEY (MatchId) REFERENCES FactTableMatch(MatchId),
    FOREIGN KEY (TeamScored) REFERENCES DimensionTeam(teamId)
);

CREATE TABLE DimDate (
    DateKey INT PRIMARY KEY,
    FullDate DATE,
    Year INT,
    Quarter INT,
    Month INT,
    Day INT
);
