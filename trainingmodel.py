import numpy as np
import functions

try:
    data = np.load("dataset.npz")
except FileNotFoundError:
    data = np.load("dataset.npz")

x_entree = data["X"] 
y = data["y"]

for i in range(6):
    col = x_entree[:, :, i]
    max_val = np.max(np.abs(col))
    if max_val > 0:
        x_entree[:, :, i] /= max_val

x_entree = x_entree.reshape(x_entree.shape[0], -1)

max_val = np.max(np.abs(x_entree))
if max_val > 0:
    x_entree = x_entree / max_val

def one_hot_encode(indices, num_classes=20):
    return np.eye(num_classes)[indices]

y_encoded = one_hot_encode(y, 20)

class Neural_Network(object):
    def __init__(self):
        self.inputSize = 120
        self.outputSize = 20
        self.hiddensize = 128

        self.W1 = np.random.randn(self.inputSize, self.hiddensize) * 0.01
        self.W2 = np.random.randn(self.hiddensize, self.hiddensize) * 0.01
        self.W3 = np.random.randn(self.hiddensize, self.outputSize) * 0.01

    def relu(self, s):
        return np.maximum(0, s)

    def reluPrime(self, s):
        s[s <= 0] = 0
        s[s > 0] = 1
        return s

    def softmax(self, s):
        exps = np.exp(s - np.max(s, axis=1, keepdims=True))
        return exps / np.sum(exps, axis=1, keepdims=True)

    def forward(self, X):
        self.z1 = np.dot(X, self.W1)
        self.a1 = self.relu(self.z1)

        self.z2 = np.dot(self.a1, self.W2)
        self.a2 = self.relu(self.z2)

        self.z3 = np.dot(self.a2, self.W3)
        o = self.softmax(self.z3) 
        return o

    def backward(self, X, y, o, lr=0.1):
        m = X.shape[0]
        
        o_delta = (o - y) / m 

        z2_error = o_delta.dot(self.W3.T)
        z2_delta = z2_error * self.reluPrime(self.a2)

        z1_error = z2_delta.dot(self.W2.T)
        z1_delta = z1_error * self.reluPrime(self.a1)

        self.W3 -= lr * self.a2.T.dot(o_delta)
        self.W2 -= lr * self.a1.T.dot(z2_delta)
        self.W1 -= lr * X.T.dot(z1_delta)

    def train(self, X, y, epochs=2000, lr=0.1):
        print(f"Entraînement sur {X.shape[0]} échantillons...")
        for i in range(epochs):
            o = self.forward(X)
            self.backward(X, y, o, lr)

            if i % 100 == 0:
                loss = -np.mean(np.sum(y * np.log(o + 1e-9), axis=1))
                
                predictions = np.argmax(o, axis=1)
                targets = np.argmax(y, axis=1)
                accuracy = np.mean(predictions == targets)
                
                print(f"Epoch: {i} - Loss (CE): {loss:.4f} - Précision: {accuracy*100:.1f}%")

if __name__ == "__main__":
    NN = Neural_Network()
    print("Démarrage de l'entraînement...")

    NN.train(x_entree, y_encoded, epochs=5000, lr=0.5)

    print("\n--- TEST RAPIDE ---")
    prediction = NN.forward(x_entree[0:1])
    node_predit = np.argmax(prediction)
    vrai_node = y[0]
    print(f"Index 0 -> Vrai: {vrai_node}, Prédit: {node_predit}")
    print(f"Confiance : {np.max(prediction)*100:.2f}%")
    functions.export_network(NN, "modele1.npz")
    print("Modèle enregistré dans modele1.npz")