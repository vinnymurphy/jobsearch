#!/usr/bin/env python

"""
Brief description of what is needed for this file
"""
from argparse import ArgumentParser, RawDescriptionHelpFormatter
import re
import random

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
MATCHUP_TEXT = """
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

def predict_winners(text):
    results = []
    lines = text.strip().split('\n')

    for line in lines:
        # Extract the first field (the matchup)
        matchup_str = line.split('|')[0].strip()

        # Regex to capture: (Rank) Team vs. (Rank) Team
        pattern = r"\((\d+)\)\s+(.*?)\s+vs\.\s+\((\d+)\)\s+(.*)"
        match = re.search(pattern, matchup_str)

        if match:
            rank1, team1 = int(match.group(1)), match.group(2).strip()
            rank2, team2 = int(match.group(3)), match.group(4).strip()

            # Logic: If seeds are within 2, choose randomly
            if abs(rank1 - rank2) <= 2:
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
    args = parse_arguments()
    predictions = predict_winners(MATCHUP_TEXT)
    for p in predictions:
        print(p)



if __name__ == "__main__":
    main()
