#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import csv
import argparse
from random import shuffle

PROPOSITIONS="propositions.csv"
PROPOSITIONS_RANDOM="propositions_random.csv"
VOTES="votes.csv"



class CourgetteEngine:

    #
    # Constructeur
    #
    def __init__(self, arg):

        self.mot = arg.mot
        self.melanger = arg.melanger
        self.rapport = arg.rapport
        self.propositions = []
        self.votes = []
        self.scrutin = {}
        self.points = {}

        self.largeur_pseudo = 15
        

            
        #
        # On mélange si ça n'a pas été fait, ou si on veut forcer le mélange
        #
        if not os.path.isfile(PROPOSITIONS_RANDOM) or self.melanger:
            self.melanger_propositions()
        
        #
        # Chargement des propositions
        #
        with open(PROPOSITIONS_RANDOM, 'r') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=';')
            for row in reader:
                self.propositions.append(row)
        
        #
        # Chargement des votes
        #
        if self.rapport == "resultats":
            with open(VOTES, 'r') as csvfile:
                reader = csv.DictReader(csvfile, delimiter=';')
                for row in reader:
                    self.votes.append(row)


                    

    def melanger_propositions(self):
        """ Génération du fichier de propositions mélangées, à partir du fichier original"""

        propositions = []
        with open(PROPOSITIONS, 'r') as orig:
            reader = csv.DictReader(orig, delimiter=';')
            for row in reader:
                propositions.append(row)

        shuffle(propositions)

        with open(PROPOSITIONS_RANDOM, 'w') as dest:
            fieldnames = ['num_prop','joueur','type_def','definition']
            writer = csv.DictWriter(dest, delimiter=';', fieldnames=fieldnames)
            writer.writeheader()
            compteur = 1
            for row in propositions:
                row['num_prop'] = compteur
                compteur += 1
                writer.writerow(row)
                

        

                
    def run(self):
        """ Point d'entrée du CourgetteEngine """

        print("""MOT : [#ff0000][b]%s[/b][/#ff0000]

"""  % self.mot.upper())

        if self.rapport == "propositions":
            self.print_propositions()

        else:

            #
            # analyse du scrutin
            #
            num_col = len(self.propositions)
            for v in self.votes:
                if not v["joueur"] in self.scrutin:
                    self.scrutin[v["joueur"]] = ["   " for x in range(num_col)]
                self.scrutin[ v["joueur"] ][ int(v["num_def"])-1 ] = " " + v["type_vote"] + " "

            #
            # décompte des points
            #

            # recherche du numéro de déf de LA_VRAIE

            vraie = int([ x["num_prop"]  for x in self.propositions if x["joueur"]=="LA_VRAIE" ][0])
            
            # initialisation du tableau des scores
            for p in self.propositions:
                if not p["joueur"] in self.points:
                    self.points[p["joueur"]] = [0,0,0,0]

            # attribution des points pour les joueurs ayant voté pour LA_VRAIE
            for s in self.scrutin:
                if self.scrutin[s][vraie - 1]==" s ":
                    self.points[s][0] = 1

            # attributions des points en fonction des votes reçus
            colonne = { 's' : 1, 'f' : 2}
            for v in self.votes:
                id_def = v["num_def"]
                joueur, type_def = [ (x["joueur"], x["type_def"]) for x in self.propositions if x["num_prop"]==id_def][0]

                self.points[joueur][colonne[type_def]] += 1
            
            # calcul des totaux par joueur
            for p in self.points:
                self.points[p][3] = sum(self.points[p][0:3])

            #
            # affichage des résultats
            #
            self.print_propositions(anonyme=False)
            self.print_votes()
            self.print_points()




            

    def print_propositions(self, anonyme=True):
        """ Affiche le BBcode des propositions
Soit de manière anonyme (avant le vote)
Soit avec les pseudos des joueurs ainsi que le type de proposition (pour
l'annonce du résultat final)
"""

        print ("[b][#001CE2]Les Définitions[/#001CE2][/b]\n\n")
        
        for p in self.propositions:

            if anonyme:
                print("[b]Définition %s[/b] %s"
                      % (p["num_prop"], p["definition"].replace('\\n','\n'))
                  )
            else:
                print("[b]Définition %s[/b] : [b][#001CE2]%s (%s)[/#001CE2][/b] : %s"
                      % (p["num_prop"], p["joueur"], p["type_def"], p["definition"])
                  )


        

    def print_votes(self):
        """ Affiche les votes """
        
        num_col = len(self.propositions)
        
        print ("\n\n[b][#001CE2]Les Votes[/#001CE2][/b][fixed]")
        print("joueur".ljust(self.largeur_pseudo) + "|P" + "|P".join([str(x+1).rjust(2,"0") for x in range(num_col)]) + "|")
        
                
        for s in self.scrutin:
            print(s.ljust(self.largeur_pseudo) + "|" + "|".join(self.scrutin[s]) + "|")

        print ("[/fixed]")


    def print_points(self):
        """ Affiche les points marqués par chaque joueurs sur cette manche """
        
        print ("\n\n[b][#001CE2]Les Points[/#001CE2][/b][fixed]")
        print("joueur".ljust(self.largeur_pseudo) + "|La Vraie|Sérieux |Fun     |Total   |")
        
                
        for p in self.points:
            print(p.ljust(self.largeur_pseudo) + "|" + "|".join([str(x).rjust(8) for x in self.points[p]]) + "|")

        print ("[/fixed]")


        
#
# Execution starts here
#
if __name__ == '__main__':

    # process command line arguments
    parser = argparse.ArgumentParser(description='Outil du MDJ pour le Jeu du dico HFR')
    
    parser.add_argument("mot", help='le mot en cours')
    parser.add_argument("rapport",choices=['propositions', 'resultats'], help='le rapport à générer')
    
    parser.add_argument('-m', '--melanger',
                        action='store_true',
                        help='forcer le mélange des propositions')

    # Runs argment parser
    arg = parser.parse_args()


    courgette = CourgetteEngine(arg)
    courgette.run()

