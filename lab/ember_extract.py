import ember
import ember
if __name__ == '__main__':
    dir='../data/EMBER_2017/'
    ember.create_vectorized_features(dir)
    ember.create_metadata(dir)