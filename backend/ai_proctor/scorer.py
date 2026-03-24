def calculate_cheat_score(eyes_away_sec, audio_spikes, multiple_faces_sec):
    # Penalties: 1pt per sec for eyes, 2pts per audio spike, 5pts per sec for extra faces
    penalty = (eyes_away_sec * 1) + (audio_spikes * 2) + (multiple_faces_sec * 5)
    return min(penalty, 100)

def calculate_integrity(cheat_score):
    return 100 - cheat_score