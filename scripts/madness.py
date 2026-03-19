#!/usr/bin/env python

"""
Bracket choices (one scenario) ...
(8) Ohio State vs. (9) TCU                    | Winner: TCU (Random Choice)
(4) Nebraska vs. (13) Troy                    | Winner: Nebraska (Higher Seed)
(6) Louisville vs. (11) South Florida         | Winner: Louisville (Higher Seed)
(5) Wisconsin vs. (12) High Point             | Winner: Wisconsin (Higher Seed)
(1) Duke vs. (16) Siena                       | Winner: Duke (Higher Seed)
(5) Vanderbilt vs. (12) McNeese               | Winner: Vanderbilt (Higher Seed)
(3) Michigan State vs. (14) North Dakota State | Winner: Michigan State (Higher Seed)
(4) Arkansas vs. (13) Hawai'i                 | Winner: Arkansas (Higher Seed)
(6) North Carolina vs. (11) VCU               | Winner: North Carolina (Higher Seed)
(1) Michigan vs. (16) Howard                  | Winner: Michigan (Higher Seed)
(6) BYU vs. (11) Texas                        | Winner: BYU (Higher Seed)
(7) Saint Mary's vs. (10) Texas A&M           | Winner: Texas A&M (Random Choice)
(3) Illinois vs. (14) Penn                    | Winner: Illinois (Higher Seed)
(8) Georgia vs. (9) Saint Louis               | Winner: Saint Louis (Random Choice)
(3) Gonzaga vs. (14) Kennesaw State           | Winner: Gonzaga (Higher Seed)
(2) Houston vs. (15) Idaho                    | Winner: Houston (Higher Seed)
(7) Kentucky vs. (10) Santa Clara             | Winner: Kentucky (Random Choice)
(5) Texas Tech vs. (12) Akron                 | Winner: Texas Tech (Higher Seed)
(1) Arizona vs. (16) Long Island University   | Winner: Arizona (Higher Seed)
(3) Virginia vs. (14) Wright State            | Winner: Virginia (Higher Seed)
(2) Iowa State vs. (15) Tennessee State       | Winner: Iowa State (Higher Seed)
(4) Alabama vs. (13) Hofstra                  | Winner: Alabama (Higher Seed)
(8) Villanova vs. (9) Utah State              | Winner: Utah State (Random Choice)
(6) Tennessee vs. (11) Miami (Ohio)           | Winner: Tennessee (Higher Seed)
(8) Clemson vs. (9) Iowa                      | Winner: Clemson (Random Choice)
(5) St. John's vs. (12) UNI                   | Winner: St. John's (Higher Seed)
(7) UCLA vs. (10) UCF                         | Winner: UCF (Random Choice)
(2) Purdue vs. (15) Queens                    | Winner: Purdue (Higher Seed)
(1) Florida vs. (16) Prairie View A&M         | Winner: Florida (Higher Seed)
(4) Kansas vs. (13) Cal Baptist               | Winner: Kansas (Higher Seed)
(2) UConn vs. (15) Furman                     | Winner: UConn (Higher Seed)
(7) Miami (Fla.) vs. (10) Missouri            | Winner: Missouri (Random Choice)
------------------------------------------------------------
(1) Duke vs. (9) TCU                          | Winner: (1) Duke (Higher Seed)
(5) St. John's vs. (4) Kansas                 | Winner: (5) St. John's (Random Choice)
(6) Louisville vs. (3) Michigan State         | Winner: (3) Michigan State (Random Choice)
(7) UCLA vs. (2) UConn                        | Winner: (2) UConn (Higher Seed)
(1) Florida vs. (8) Clemson                   | Winner: (1) Florida (Higher Seed)
(5) Vanderbilt vs. (4) Nebraska               | Winner: (5) Vanderbilt (Random Choice)
(6) North Carolina vs. (3) Illinois           | Winner: (3) Illinois (Random Choice)
(7) Saint Mary's vs. (2) Houston              | Winner: (2) Houston (Higher Seed)
(1) Arizona vs. (9) Utah State                | Winner: (1) Arizona (Higher Seed)
(5) Wisconsin vs. (4) Arkansas                | Winner: (4) Arkansas (Random Choice)
(6) BYU vs. (3) Gonzaga                       | Winner: (3) Gonzaga (Random Choice)
(7) Miami (Fla.) vs. (2) Purdue               | Winner: (2) Purdue (Higher Seed)
(1) Michigan vs. (9) Saint Louis              | Winner: (1) Michigan (Higher Seed)
(5) Texas Tech vs. (4) Alabama                | Winner: (4) Alabama (Random Choice)
(6) Tennessee vs. (3) Virginia                | Winner: (3) Virginia (Random Choice)
(7) Kentucky vs. (2) Iowa State               | Winner: (2) Iowa State (Higher Seed)
------------------------------------------------------------
(1) Duke vs. (5) St. John's                   | Winner: (1) Duke (Higher Seed)
(3) Michigan State vs. (2) UConn              | Winner: (3) Michigan State (Random Choice)
(1) Florida  vs. (5) Vanderbilt               | Winner: (1) Florida (Higher Seed)
(3) Illinois vs. (2) Houston                  | Winner: (2) Houston (Random Choice)
(1) Arizona  vs. (4) Arkansas                 | Winner: (1) Arizona (Random Choice)
(3) Gonzaga  vs. (2) Purdue                   | Winner: (3) Gonzaga (Random Choice)
(1) Michigan vs. (4) Alabama                  | Winner: (1) Michigan (Random Choice)
(3) Virginia  vs. (2) Iowa State              | Winner: (2) Iowa State (Random Choice)
------------------------------------------------------------
(1) Duke vs. (3) Michigan State               | Winner: Michigan State (Random Choice)
(1) Florida vs. (2) Houston                   | Winner: Florida (Random Choice)
(1) Arizona vs. (3) Gonzaga                   | Winner: Arizona (Random Choice)
(1) Michigan vs. (2) Iowa State               | Winner: Iowa State (Random Choice)
------------------------------------------------------------
(1) Michigan State vs. (1) Florida            | Winner: Michigan State (Random Choice)
(1) Arizona vs. (2) Iowa State                | Winner: Arizona (Random Choice)
------------------------------------------------------------
(1) Michigan State vs. (1) Arizona            | Winner: Michigan State (Random Choice)

"""

import random
import re
from argparse import ArgumentParser, RawDescriptionHelpFormatter


def parse_arguments():
    """Parses command-line arguments

    Returns the parsed arguments

    Returns:
        Namespace: Parsed arguments
    """
    desc = __import__("__main__").__doc__
    parser = ArgumentParser(
        formatter_class=RawDescriptionHelpFormatter, description=desc
    )
    return parser.parse_args()


# The list of matchups
MATCHUP1_TEXT = """
(8) Ohio State vs. (9) TCU | 12:15 p.m. | CBS
(4) Nebraska vs. (13) Troy | 12:40 p.m. | truTV
(6) Louisville vs. (11) South Florida | 1:30 p.m. | TNT
(5) Wisconsin vs. (12) High Point | 1:50 p.m. | TBS
(1) Duke vs. (16) Siena | 2:50 p.m. | CBS
(5) Vanderbilt vs. (12) McNeese | 3:15 p.m. | truTV
(3) Michigan State vs. (14) North Dakota State | 4:05 p.m. | TNT
(4) Arkansas vs. (13) Hawai'i | 4:25 p.m. | TBS
(6) North Carolina vs. (11) VCU | 6:50 p.m. | TNT
(1) Michigan vs. (16) Howard | 7:10 p.m. | CBS
(6) BYU vs. (11) Texas | 7:25 p.m. | TBS
(7) Saint Mary's vs. (10) Texas A&M | 7:35 p.m. | truTV
(3) Illinois vs. (14) Penn | 9:25 p.m. | TNT
(8) Georgia vs. (9) Saint Louis | 9:45 p.m. | CBS
(3) Gonzaga vs. (14) Kennesaw State | 10 p.m. | TNT
(2) Houston vs. (15) Idaho | 10:10 p.m. | truTV
(7) Kentucky vs. (10) Santa Clara | 12:15 p.m. | CBS
(5) Texas Tech vs. (12) Akron | 12:40 p.m. | truTV
(1) Arizona vs. (16) Long Island University | 1:35 p.m. | TNT
(3) Virginia vs. (14) Wright State | 1:50 p.m. | TBS
(2) Iowa State vs. (15) Tennessee State | 2:50 p.m. | CBS
(4) Alabama vs. (13) Hofstra | 3:15 p.m. | truTV
(8) Villanova vs. (9) Utah State | 4:10 p.m. | TNT
(6) Tennessee vs. (11) Miami (Ohio) | 4:25 p.m. | TBS
(8) Clemson vs. (9) Iowa | 6:50 p.m. | TNT
(5) St. John's vs. (12) UNI | 7:10 p.m. | CBS
(7) UCLA vs. (10) UCF | 7:25 p.m. | TBS
(2) Purdue vs. (15) Queens | 7:35 p.m. | truTV
(1) Florida vs. (16) Prairie View A&M | 9:25 p.m. | TNT
(4) Kansas vs. (13) Cal Baptist | 9:45 p.m. | CBS
(2) UConn vs. (15) Furman | 10 p.m. | TBS
(7) Miami (Fla.) vs. (10) Missouri | 10:10 p.m. | truTV
"""
MATCHUP2_TEXT = """
(1) Duke vs. (9) TCU |
(5) St. John's vs. (4) Kansas |
(6) Louisville vs. (3) Michigan State|
(7) UCLA vs. (2) UConn |
(1) Florida vs. (8) Clemson|
(5) Vanderbilt vs. (4) Nebraska|
(6) North Carolina vs. (3) Illinois|
(7) Saint Mary's vs. (2) Houston |
(1) Arizona vs. (9) Utah State |
(5) Wisconsin vs. (4) Arkansas |
(6) BYU vs. (3) Gonzaga |
(7) Miami (Fla.) vs. (2) Purdue |
(1) Michigan vs. (9) Saint Louis |
(5) Texas Tech vs. (4) Alabama |
(6) Tennessee vs. (3) Virginia |
(7) Kentucky vs. (2) Iowa State |
"""

MATCHUP3_TEXT = """
(1) Duke vs. (5) St. John's |
(3) Michigan State vs. (2) UConn  |
(1) Florida  vs. (5) Vanderbilt |
(3) Illinois vs. (2) Houston  |
(1) Arizona  vs. (4) Arkansas |
(3) Gonzaga  vs. (2) Purdue |
(1) Michigan vs. (4) Alabama |
(3) Virginia  vs. (2) Iowa State |
"""

MATCHUP4_TEXT = """
(1) Duke vs. (3) Michigan State |
(1) Florida vs. (2) Houston  |
(1) Arizona vs. (3) Gonzaga |
(1) Michigan vs. (2) Iowa State |
"""

MATCHUP5_TEXT = """
(1) Michigan State vs. (1) Florida |
(1) Arizona vs. (2) Iowa State |
"""
MATCHUP6_TEXT = """
(1) Michigan State vs. (1) Arizona |
"""


def predict_winners(text):
    results = []
    lines = text.strip().split("\n")
    seeds_within = 3

    for line in lines:
        # Extract the first field (the matchup)
        matchup_str = line.split("|")[0].strip()

        # Regex to capture: (Rank) Team vs. (Rank) Team
        pattern = r"\((\d+)\)\s+(.*?)\s+vs\.\s+\((\d+)\)\s+(.*)"
        match = re.search(pattern, matchup_str)

        if match:
            rank1, team1 = int(match.group(1)), match.group(2).strip()
            rank2, team2 = int(match.group(3)), match.group(4).strip()

            # Logic: If seeds are within 2, choose randomly
            if abs(rank1 - rank2) <= seeds_within:
                winner = random.choice([team1, team2])
                method = "Random Choice"
            else:
                # Select the smaller seed number (higher rank)
                winner = team1 if rank1 < rank2 else team2
                method = "Higher Seed"

            results.append(f"{matchup_str:45} | Winner: {winner} ({method})")

    return results


# Run the prediction


def main():
    """run the main function"""
    for predict in [
        MATCHUP1_TEXT,
        MATCHUP2_TEXT,
        MATCHUP3_TEXT,
        MATCHUP4_TEXT,
        MATCHUP5_TEXT,
        MATCHUP6_TEXT,
    ]:
        predictions = predict_winners(predict)
        for p in predictions:
            print(p)
        print("-" * 33)


if __name__ == "__main__":
    main()
