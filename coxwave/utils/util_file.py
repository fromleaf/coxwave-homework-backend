import pickle


def load_pickle_file(filepath):
    with open(filepath, 'rb') as f:
        faq_data = pickle.load(f)
    return faq_data
