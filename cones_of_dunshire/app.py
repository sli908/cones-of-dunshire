#!/usr/bin/env python3
from flask import Flask, render_template, flash, request, redirect, url_for, session
try:
    from player import Player, Role, Resource
except:
    from .player import Player, Role, Resource
import random

app = Flask(__name__)
app.secret_key = b'i\'m the maverick'

deck = list(range(1, 26))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/go_to_sleep')
def sleep():
    return render_template('sleep.html')

@app.route('/menu', methods=["POST"])
def main_menu():
    if request.form.get('hand', False):
        return redirect(url_for('hand'))
    elif request.form.get('new_game', False):
        session['player_ct'] = 0
        return redirect(url_for('player_setup'))

@app.route('/hand')
def hand():
    if not session.get('cards', False):
        session['cards'] = []
        session['next_card'] = 0

    return render_template('hand.html', cards=session['cards'])

@app.route('/hand', methods=["POST"])
def draw():
    if request.form.get('draw', False):
        new_card = {
            'id': "card" + str(session['next_card']),
            'text': random.choice(deck),
        }
        session['cards'].append(new_card)
        session['next_card'] += 1
    elif request.form.get('clear', False):
        session['cards'] = []
        session['next_card'] = 0

    return redirect(url_for('hand'))

@app.route('/remove_card', methods=["POST"])
def remove_card():
    new_cards = []
    for card in session['cards']:
        name = card['id']
        if not request.form.get(name, False):
            new_cards.append(card)
    session['cards'] = new_cards

    return redirect(url_for('hand'))

@app.route('/player_setup', methods=["GET"])
def player_setup():
    return render_template(
        "player_setup.html",
        roles=list(Role),
        players=range(session['player_ct']),
    )

@app.route('/player_setup', methods=["POST"])
def player_form():
    if request.form.get('add_player', False):
        session['player_ct'] += 1
        return redirect(url_for('player_setup'))
    elif request.form.get('submit', False):
        session['players'] = []
        for i in range(session['player_ct']):
            session['players'].append(
                Player(
                    i,
                    request.form[f'player_{i}'],
                    Role(int(request.form[f'player_{i}_role'])),
                ).to_json()
            )
        session['dice_3'] = []
        session['dice'] = []
        return redirect(url_for('game'))
    elif request.form.get('delete_players', False):
        session['player_ct'] = 0
        return redirect(url_for('player_setup'))

@app.route('/game')
def game():
    return render_template(
        'game.html',
        players=[Player.from_json(x) for x in session['players']],
        dice_3=session['dice_3'],
        dice=session['dice'],
        dice_total=sum(session['dice_3']),
        resources=list(Resource),
    )

@app.route('/roll', methods=['POST'])
def dice_roll():
    session['dice_3'] = [
        random.randint(1, 6) for _ in range(3)
    ]
    dice_ct = sum(session['dice_3'])
    session['dice'] = [
        random.randint(1, 6) for _ in range(dice_ct)
    ]
    return redirect(url_for('game'))

@app.route('/resource_update/<int:player>/<int:resource>', methods=['POST'])
def resource_update(player, resource):
    p = Player.from_json(session['players'][player])
    if request.form.get('plus', False):
        p.resources[resource] += 1
    elif request.form.get('minus', False):
        p.resources[resource] -= 1
    elif request.form.get('reset', False):
        p.resources[resource] = 0
    session['players'][player] = p.to_json()
    session.modified = True # Since we modify a mutable object
    return redirect(url_for('game'))

if __name__ == "__main__":
    app.run()
