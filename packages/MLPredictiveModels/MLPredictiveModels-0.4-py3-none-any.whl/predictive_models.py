import numpy as np 
from tqdm import tqdm
class LinearRegression ():
    def __init__ (self):
        self.parameters = {}
    
    def forward_pass(self,train_input):
        # y = m * x + b
        m = self.parameters.get('m')
        b = self.parameters.get('b')
        predictions = (m* train_input) + b
        return predictions
    
    def backward_pass(self,train_input,train_output,predictions):
        # calculate the derivatives 
        derivatives = {}
        # m = slope , b  = intercept
        # df/dm = 2 * mean((y - y_hat) * x)
        df = predictions - train_output 
        dm = 2 * np.mean(df * train_input)
        dc = 2 * np.mean(df)
        derivatives['m'] = dm
        derivatives['b'] = dc
        return derivatives
    
    def update_parameters(self,derivatives,learning_rate):
        # update the parameters 
        self.parameters['m'] = self.parameters['m'] - learning_rate * derivatives['m']
        self.parameters['b'] = self.parameters['b'] - learning_rate * derivatives['b']
    def fit(self,train_input,train_output,learning_rate ,epochs):
        #initialize the parameters 
        self.parameters['m'] = np.random.uniform(0,1)*-1
        self.parameters['b'] = np.random.uniform(0,1)*-1

        self.loss = []
        self.accuracy = []
        for epoch in tqdm(range(epochs)):
            predictions = self.forward_pass(train_input)
            derivatives = self.backward_pass(train_input,train_output,predictions)
            self.update_parameters(derivatives , learning_rate)
            loss = np.mean(predictions - train_output)**2
            accuracy = np.mean(np.abs(predictions - train_output) < 0.1) * 100
            self.loss.append(loss)
            self.accuracy.append(accuracy)
            print(f'Epoch {epoch+1}/{epochs}, Loss: {loss:.4f}', 'Accuracy: {:.2f}%'.format(accuracy))
        return self.parameters , np.mean(self.loss) , np.mean(self.accuracy)
    def predict(self, test_input):
        return self.forward_pass(test_input)
    def evaluate(self, test_input, test_output):
        predictions = self.forward_pass(test_input)
        mse = np.mean((test_output - predictions) ** 2)
        # r2 optional
        r2 = 1 - np.sum((test_output - predictions) ** 2) / np.sum((test_output - np.mean(test_output)) ** 2)
        accuracy = np.mean(np.abs(predictions - test_output) < 0.1) * 100
        return mse, r2 , accuracy 



class LassoRegression:
    def __init__(self, learning_rate=0.01, iterations=1000, l1_penalty=0.1):
        self.learning_rate = learning_rate
        self.iterations = iterations
        self.l1_penalty = l1_penalty

    def fit(self, X, Y):
        self.m, self.n = X.shape
        self.W = np.zeros(self.n)
        self.b = 0
        self.X = X
        self.Y = Y
        
        for i in tqdm(range(self.iterations)):
            self.update_weights()
            
            Y_pred = self.predict(self.X)
            loss = np.mean((self.Y - Y_pred) ** 2)
            accuracy = np.mean(np.abs(Y_pred - self.Y) < 0.1) * 100
            print(f'Iteration {i+1}/{self.iterations}, Loss: {loss:.4f}, Accuracy: {accuracy:.2f}%')
            
        return self

    def update_weights(self):
        Y_pred = self.predict(self.X)
        dW = np.zeros(self.n)

        for j in range(self.n):
            gradient = -2 * (self.X[:, j]).dot(self.Y - Y_pred) / self.m
            if self.W[j] > 0:
                dW[j] = gradient + self.l1_penalty
            else:
                dW[j] = gradient - self.l1_penalty

        db = -2 * np.sum(self.Y - Y_pred) / self.m

        self.W -= self.learning_rate * dW
        self.b -= self.learning_rate * db

    def predict(self, X):
        return X.dot(self.W) + self.b

    def evaluate(self, X, Y):
        Y_pred = self.predict(X)
        mse = np.mean((Y - Y_pred) ** 2)
        r2 = 1 - np.sum((Y - Y_pred) ** 2) / np.sum((Y - np.mean(Y)) ** 2)
        accuracy = np.mean(np.abs(Y_pred - Y) < 0.1) * 100
        return mse, r2, accuracy


class RidgeRegression():
    def __init__ (self , learning_rate ,  epochs , l2_penalty ):
        self.learning_rate = learning_rate 
        self.epochs = epochs 
        self.l2_penalty = l2_penalty 

    def fit(self, X,Y):
        self.m , self.n = X.shape 
        self.W = np.zeros(self.n)
        self.b=0
        self.X = X
        self.Y = Y
        
        for i in tqdm(range(self.epochs)):
            self.update_weights()
            Y_pred = self.predict(self.X)
            loss = np.mean(self.Y - Y_pred)**2 + self.l2_penalty * np.sum(self.W ** 2)
            accuracy = np.mean(np.abs(Y_pred - self.Y)<0.1) *100
            print(f'Epoch {i+1}/{self.epochs}, Loss: {loss:.4f}, Accuracy: {accuracy:.2f}%')
        return self
    def update_weights(self):
        Y_pred = self.predict(self.X)
        dW = ( - ( 2 * ( self.X.T ).dot( self.Y - Y_pred ) ) +               
               ( 2 * self.l2_penalty * self.W ) ) / self.m     
        db = - 2 * np.sum( self.Y - Y_pred ) / self.m
        self.W -= self.learning_rate * dW
        self.b -= self.learning_rate * db
    def predict(self,X):
        return X.dot(self.W) + self.b
    def evaluate(self, X, Y):
        Y_pred = self.predict(X)
        mse = np.mean((Y - Y_pred) ** 2)
        r2 = 1 - np.sum((Y - Y_pred) ** 2) / np.sum((Y - np.mean(Y)) ** 2)
        accuracy = np.mean(np.abs(Y_pred - Y) < 0.1) * 100
        return mse, r2, accuracy

class PolynomialRegression:
    def __init__(self, degree=2, learning_rate=0.01, epochs=1000):
        self.degree = degree
        self.learning_rate = learning_rate
        self.epochs = epochs
        self.parameters = None

    def fit(self, X, Y):
        X_poly = np.vander(X.flatten(), self.degree + 1, increasing=True)
        self.parameters = np.zeros(X_poly.shape[1])
        
        for epoch in tqdm(range(self.epochs)):
            predictions = X_poly.dot(self.parameters)
            errors = predictions - Y
            
            gradients = (2 / len(Y)) * X_poly.T.dot(errors)
            self.parameters -= self.learning_rate * gradients
            
            loss = np.mean(errors ** 2)
            accuracy = np.mean(np.abs(predictions - Y) < 0.1) * 100
            print(f'Epoch {epoch + 1}/{self.epochs}, Loss: {loss:.4f}, Accuracy: {accuracy:.2f}%')
        
        return self

    def predict(self, X):
        X_poly = np.vander(X.flatten(), self.degree + 1, increasing=True)
        return X_poly.dot(self.parameters)

    def evaluate(self, X, Y):
        predictions = self.predict(X)
        mse = np.mean((Y - predictions) ** 2)
        r2 = 1 - np.sum((Y - predictions) ** 2) / np.sum((Y - np.mean(Y)) ** 2)
        accuracy = np.mean(np.abs(predictions - Y) < 0.1) * 100
        return mse, r2, accuracy

# Decision Tree Regressor
# Nodes 
class Node():
    def __init__(self, feature_index = None , threshold = None ,left = None , right = None ,value = None):
        self.feature_index = feature_index
        self.threshold = threshold
        self.left = left
        self.right = right
        self.value = value

# Decision Tree Regressor
class DecisionTreeRegressor():
    def __init__(self, min_samples_split= 3 , max_depth= 5):
        self.root = None 
        self.min_samples_split = min_samples_split
        self.max_depth = max_depth
    
    def build_tree(self,X,Y,depth = 0):
        m ,n  = X.shape
        best_split = {}
        if m >= self.min_samples_split and depth < self.max_depth:
            best_feature_index, best_threshold = self.best_split(X, Y)
            if best_feature_index is not None:
                left_indices = X[:, best_feature_index] < best_threshold
                right_indices = X[:, best_feature_index] >= best_threshold
                
                left_node = self.build_tree(X[left_indices], Y[left_indices], depth + 1)
                right_node = self.build_tree(X[right_indices], Y[right_indices], depth + 1)
                
                return Node(feature_index=best_feature_index, threshold=best_threshold, left=left_node, right=right_node)
        return Node(value=np.mean(Y))  
    def best_split(self, X, Y):
        m,n = X.shape
        best_mse = float('inf')
        best_feature_index = None 
        best_threshold = None

        for feature_index in tqdm(range(n)):
            thresholds = np.unique(X[:, feature_index])
            for threshold in thresholds:
                left_indices = X[:, feature_index] < threshold
                right_indices = X[:, feature_index] >= threshold
                
                if np.sum(left_indices) == 0 or np.sum(right_indices) == 0:
                    continue
                
                left_Y = Y[left_indices]
                right_Y = Y[right_indices]
                
                mse = self.calculate_mse(left_Y, right_Y)
                
                if mse < best_mse:
                    best_mse = mse
                    best_feature_index = feature_index
                    best_threshold = threshold

        return best_feature_index, best_threshold
    def calculate_mse(self , left_Y , right_Y):
        left_mse = np.mean((left_Y - np.mean(left_Y))**2)
        right_mse = np.mean((right_Y - np.mean(right_Y))**2)
        return (left_mse * len(left_Y) + right_mse * len(right_Y)) / (len(left_Y) + len(right_Y))
    # fit the data 
    def fit(self,X,Y):
        self.root = self.build_tree(X,Y)
        return self
    # predict the data
    def predict(self, X):
        predictions = []
        for x in X:
            node = self.root
            while node.value is None:
                if x[node.feature_index] < node.threshold:
                    node = node.left
                else:
                    node = node.right
            predictions.append(node.value)
        return np.array(predictions)
    def evaluate(self, X, Y):
        predictions = self.predict(X)
        mse = np.mean((Y - predictions) ** 2)
        r2 = 1 - np.sum((Y - predictions) ** 2) / np.sum((Y - np.mean(Y)) ** 2)
        accuracy = np.mean(np.abs(predictions - Y) < 0.1) * 100
        return mse, r2, accuracy

# Example usage
if __name__ == "__main__":
    x_train = np.array([[1],[2],[3],[4],[5]])
    y_train = np.array([1.5, 2.5, 3.5, 4.5, 5.5])
    
    model = DecisionTreeRegressor(min_samples_split=2, max_depth=3)
    model.fit(x_train, y_train)
    predictions = model.predict(x_train)
    mse, r2, accuracy = model.evaluate(x_train, y_train)
    print(f"Predictions: {predictions}")
    print(f"MSE: {mse}, R2: {r2}, Accuracy: {accuracy:.2f}%")

class SVR():
    def __init__(self, C=1.0, epsilon=0.1, lr=0.01, n_iters=1000):
        self.C = C
        self.epsilon = epsilon
        self.lr = lr
        self.n_iters = n_iters
    
    def fit(self,X,Y):
        n_samples, n_features = X.shape
        self.w = np.zeros(n_features)
        self.b=0
        
        for _ in tqdm(range(self.n_iters)):
            y_pred = self.predict(X)
            error = Y - y_pred

            loss_grad = np.zeros_like(self.w)
            b_grad = 0

            for i in tqdm(range(n_samples)):
               if abs(error[i]) > self.epsilon:
                    sign = -1 if error[i] < 0 else 1
                    loss_grad += -self.C * sign * X[i]
                    b_grad += -self.C * sign
            # regularization
            loss_grad += self.w

            self.w -= self.lr * loss_grad
            self.b -= self.lr * b_grad
    
    def predict(self,X):
        return np.dot(X, self.w) + self.b
    def evaluate(self, X, Y):
        predictions = self.predict(X)
        mse = np.mean((Y - predictions) ** 2)
        r2 = 1 - np.sum((Y - predictions) ** 2) / np.sum((Y - np.mean(Y)) ** 2)
        accuracy = np.mean(np.abs(predictions - Y) < 0.1) * 100
        return mse, r2, accuracy

class RandomForestRegressor():
    def __init__(self,n_estimators = 100, max_depth = None, min_samples_split = 2):
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.trees = []
    
    def fit(self,X,Y):
        n_samples, n_features = X.shape
        for _ in tqdm(range(self.n_estimators)):
            indices = np.random.choice(n_samples, n_samples, replace=True)
            X_sample = X[indices]
            Y_sample = Y[indices]
             
            tree = DecisionTreeRegressor(min_samples_split=self.min_samples_split, max_depth=self.max_depth)
            tree.fit(X_sample, Y_sample)
            self.trees.append(tree)
        
    def predict(self, X):
            predictions = np.zeros((X.shape[0], self.n_estimators))
            for i, tree in tqdm(enumerate(self.trees)):
                predictions[:, i] = tree.predict(X)
            return np.mean(predictions, axis=1)
    def evaluate(self, X, Y): 
        predictions = self.predict(X)
        mse = np.mean((Y - predictions) ** 2)
        r2 = 1 - np.sum((Y - predictions) ** 2) / np.sum((Y - np.mean(Y)) ** 2)
        accuracy = np.mean(np.abs(predictions - Y) < 0.1) * 100
        return mse, r2, accuracy


        

