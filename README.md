# IA de prédiction de pannes de composants informatiques


De Mathis Toba


# Explications du scénario


## Informations générales

Mon projet consiste à réaliser une intelligence artificielle capable de prédir la panne d'un composant dans un circuit électronique.

Un système électronique est représenté par un réseau de nœuds interconnectés. Chaque nœud représente un composant du système. 

Ce système évolue dans le temps, et peut comporter des pannes. Le calcul des pannes sera défini ultérieurement. Plus le temps évolue, et plus les pannes apparaissent. L’état d’un composant dépendra aussi de l’état des composants reliés à celui-ci.


## Etat du composant


### Risque de défaillance


Pour déterminer le risque de défaillance, on définit un score de risque lié à des variables physiques comme la température, le vieillissement comme suit:


$$
R_i(t) = \alpha L_i(t) + \beta \frac{T_i(t)}{T_{\max}} + \gamma \frac{A_i(t)}{A_{\max}} + \delta \cdot \frac{1}{|N(i)|} \sum_{j \in N(i)} F_j(t)
$$


Pour plus de détailles sur les fonctions, voir la page suivante:


## Risque de défaillance

Chaque fonction ici est une indication phsysique calculée comme suit: 


$$
R_i(t) = \alpha L_i(t) + \beta \frac{T_i(t)}{T_{\max}} + \gamma \frac{A_i(t)}{A_{\max}} + \delta \cdot \frac{1}{|N(i)|} \sum_{j \in N(i)} F_j(t)
$$


## Influence des voisins: 


$$
 \delta \cdot \frac{1}{|N(i)|} \sum_{j \in N(i)} F_j(t)
$$


C’est la formule la plus simple, |N(i)| représente le nombre de voisins et Fj représente l’état du voisin (0 ou 1) si il est défaillant ou pas.


## La charge:


$$
 \alpha L_i(t) 
$$


La charge représente l’utilisation du composant, plus il est utilisé et plus il est surchargé, donc peut faire des erreurs.


Formule de la charge: 


$$
L_i(t) = L_{\text{base}}(t) \cdot (1 + k_{\text{report}} \cdot S_i(t)) + \epsilon
$$


Cette formule prend en compte l’influence des voisins, qui augmente la surcharge à mesures que les composants voisins deviennent défectueux selon le coef $k_{\text report}$ qu’on définira avec les autres variables.


$L_{\text base}(t)$ est la charge nominale du composant par défaut, elle sera représentée par une sinusoïde. 


$\epsilon$ est une constante qui ajoute un peu de bruit aléatoirement.


## La température:


$$
T_i(t) = T_i(t-1) + \underbrace{a \cdot (L_i(t))^2}_{\text{Effet Joule}} - \underbrace{b \cdot (T_i(t-1) - T_{\text{amb}})}_{\text{Refroidissement}} + \underbrace{c \sum_{j \in N(i)} (T_j(t-1) - T_i(t-1))}_{\text{Diffusion thermique}}
$$


L’évolution de la température se fera en fonction de la température précédente à laquelle on ajoutera l’effet joule, la diffusion thermique ainsi que le refroidissement


### Effet joule


L’effet joule sera un facteur lié à la surcharge, en effet plus le composant utilise d’électricité, et plus il chauffe par effet joule


### Refroidissement 


Le refroidissement vient pour rééquilibrer le tout, il dépend de la température ambiante


### Diffusion thermique


La diffusion thermique ajoute de la chaleur si les voisins j sont plus chaud que le composant i


## Âge


$$
A_i(t) = A_i(t-1) + \Delta t \cdot \text{AF}_i(t)
$$


Pour quantifier la dégradation du composant liée à son âge, on utilise le modèle d’Arrhenius. Ce modèle est utile pour décrire la situation interne du composant, qui varie avec le temps et la température. En effet, la température engendre de la dilatation thermique, qui fait varier le volume des composants internes. Une différence de température entraîne donc une différence de volume entre certains composants et engendre un cisaillement dans les joints de soudure. Les réactions chimiques, la diffusion des gaz et des liquides, ainsi que certains autres processus physiques sont accélérés par l’augmentation de la température. La loi d’Arrhenius sert justement à décrire ce phénomène.


En savoir plus sur:  [Practical Reliability Engineering](https://vibadirect.com/koolinks/documents/practical-reliability-engineering.pdf) de Patrick D. T. O'Connor (source page 238-239)


Le facteur d’accélération du Modèle d'Arrhenius sera donné par:


$$
\text{AF}_i(T) = \exp \left[ \frac{E_a}{k_B} \left( \frac{1}{T_{\text{ref}}} - \frac{1}{T_i(t)} \right) \right]
$$


## Liste des variables à définir pour chaque composant:

- $\alpha$ (1.0, 3.0)
- $\beta$ (2.0, 5.0)
- $\gamma$ (1.0, 4.0)
- $\delta$ (2.0, 6.0)
- $\Delta t$ (1)

### Charge

- $L_{\text{base}}(t) = A \sin(wt) + B$

Donc

- A (10,30)
- B (40,60)
- $\omega$ (0.05, 0.2)
- $k_{\text report} (0.2, 0.5)$
- $\epsilon$ (-2.0, 2.0)

### Température

- $T_{\text{amb}}$ (20,25) fixe
- a (0.001, 0.003)
- b (0.05, 0.15)
- c (0.01, 0.05)
- $T_{max}$ (85, 120)

### Âge

- $E_a$(0.4, 0.7)
- $k_B$(8.617e-5)
- $T_{ref} $ (298.15)
- $A_{max}$ (2000,5000)

### Loi de défaillance


On utilisera une loi de défaillance probabiliste afin d’être le plus réaliste possible


$$
P(F_i(t+\Delta t)=1)=\sigma(R_i(t))
$$


Pour plus de détails, voir:


## Loi de défaillance

La loi de défaillance est donnée par:


$$
P(F_i(t+\Delta t)=1)=\sigma(R_i(t))
$$


Vu qu’il s’agit d’une probabilité, on va utiliser la fonction sigmoïde décalée pour obtenir une valeur entre 0 et 1. 


donc 


$$
\sigma(x)=\frac{1}{1+e^{-x-Seuil}}
$$


## Dynamique temporelle


A chaque pas de temps, le système évolue:

- Mise à jour des charges
- Diffusion thermique sur les voisins
- Mise à jour des pannes

## Représentation graphique 


On peut représenter le problème comme un graphe connexe non pondéré qui évolue dans le temps. A un temps t, le graphique peut ressembler à ça:


![Aperçu](assets/image.png)


Les nœuds vert représentent les composants en bon état


Les nœuds orange représentent les composants en surchauffe


Les nœuds rouge représentent les composants défectueux


# Objectif de l’IA


L’objectif de l’intelligence artificielle va être de prévoir sur quel nœud sera la prochaine panne. 


## Modèle utilisé


On va réaliser un réseau de neurones simple, basé sur $n \cdot6$ neurones d’entrée (car il y a 6 features par nœud), deux couches de 128 neurones cachés et 20 neurones de sorties. Elle sera entraînée à partir de milliers de simimations réalisées au préalable.


## Explications sur le modèle

## Explications préliminaires et problèmes rencontrés


Avant d’obtenir un modèle fonctionnel,  j’ai du faire face à énormément d’erreurs qui m’ont permis d’en apprendre plus sur le fonctionnement de l’IA en général.


La première erreur a été de créer un jeu de données basées sur des simulations avec des poids différents. Etant donné que chaque simulation était aléatoire, l’IA ne pouvait pas apprendre et restée bloquée sur une précision de 0.05 (soit 1/20). Ce qui revient à choisir aléatoirement un nœud. J’ai donc modifié le jeu de données afin de réaliser des simulations à mêmes paramètres, en changeant uniquement la topologie du graph de composants.


En appliquant cette modification, je ne tombait plus sur la précision de 0.05 mais sur une précision de 0.04748 (exactement et systématiquement). Mais alors pourquoi ce nombre exactement ?


### MSE + sigmoïde vs Cross Entropy + Softmax


Jusque là, pour calculer l’erreur j’utilisais MSE (mean square error) calculée avec


 $\text{MSE} = \frac{1}{n} \sum_{i=1}^{n} (Y_i - \hat{Y}_i)^2$ . Pour calculer les poids des neurones, j’utilisais la fonction sigmoïde, ce qui donnait des gradients faibles, rend l’apprentissage lent voir le bloque (ce qui donne une précision de 0.04748 correspondant à la mouenne quadratique donnée par $MSE = \frac{1}{20} \times [ (1 - 0.05)^2 + 19 \times (0 - 0.05)^2 ] \approx \mathbf{0.0475}$). En réalité la fonction sigmoïde n’est pas adaptée pour un problème comme celui-ci avec plusieurs neurones en sortie. De plus, l’utilisation de la fonction sigmoïde en sortie pose problème lorsque plusieurs neurones de sortie sont présents. Chaque neurone étant traité indépendamment, aucune contrainte n’impose qu’une seule classe soit prédite. Par ailleurs, la sigmoïde souffre d’un phénomène de saturation : lorsque les sorties sont proches de 0 ou de 1, les gradients deviennent très faibles, ce qui ralentit considérablement l’apprentissage.

À l’inverse, la fonction Softmax est spécifiquement conçue pour les problèmes de classification multi-classes. Elle transforme les sorties du réseau en une distribution de probabilité normalisée dont la somme vaut 1, introduisant ainsi une compétition entre les classes.

Associée à la fonction de coût Cross-Entropy, cette architecture permet d’optimiser directement la probabilité de la classe correcte. La Cross-Entropy pénalise fortement les prédictions incorrectes mais confiantes, et son gradient est plus stable, ce qui améliore la vitesse et la fiabilité de l’apprentissage.

Ainsi, l’architecture Cross-Entropy + Softmax est beaucoup mieux adaptée à ce projet que la combinaison MSE + sigmoïde.

