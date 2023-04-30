import math

import numpy as np
from sklearn.utils import check_random_state
from sklearn.utils.validation import check_is_fitted

from metric_learn.scml import _BaseSCML



class _BaseSCMLNoCheck(_BaseSCML):

    '''
    fit, but without the input checking.
    input checking reconstitutes the original array when a preprocessor is
    used for some reason
    '''
    def _fit(self, triplets, basis=None, n_basis=None):
        """
        Optimization procedure to find a sparse vector of weights to
        construct the metric from the basis set. This is based on the
        dual averaging method.
        """

        if not isinstance(self.max_iter, int):
            raise ValueError("max_iter should be an integer, instead it is of type"
                            " %s" % type(self.max_iter))
        if not isinstance(self.output_iter, int):
            raise ValueError("output_iter should be an integer, instead it is of "
                            "type %s" % type(self.output_iter))
        if not isinstance(self.batch_size, int):
            raise ValueError("batch_size should be an integer, instead it is of type"
                            " %s" % type(self.batch_size))

        if(self.output_iter > self.max_iter):
            raise ValueError("The value of output_iter must be equal or smaller than"
                            " max_iter.")

        # remove the triplet check because it reconstitutes the original
        # tuple array (???) rather than checking the points array and index array
        # in conjunction
        # if the arrays are sufficiently large then this throws a MemoryError
        # from trying to create an array with several tens of gigabytes
        
        # triplets = self._prepare_inputs(triplets, type_of_inputs='tuples')
        
        # have to replace with the non-checking portions of _prepare_inputs()
        # this NEEDS a preprocessor
        self._check_preprocessor()
        check_is_fitted(self, ['preprocessor_'])
        if not hasattr(self, 'n_features_in_'):
            self.n_features_in_ = self.preprocessor.shape[1]

        X = self.preprocessor

        if basis is None:
            basis, n_basis = self._initialize_basis(triplets, X)

        # i've changed dist_diff to be a callable object that
        # can be used to retrieve a single distance difference,
        # given an index
        dist_diff = self._compute_dist_diff(triplets, X, basis)

        n_triplets = triplets.shape[0]

        # weight vector
        w = np.zeros((1, n_basis))
        # avarage obj gradient wrt weights
        avg_grad_w = np.zeros((1, n_basis))

        # l2 norm in time of all obj gradients wrt weights
        ada_grad_w = np.zeros((1, n_basis))
        # slack for not dividing by zero
        delta = 0.001

        best_obj = np.inf

        rng = check_random_state(self.random_state)
        rand_int = rng.randint(low=0, high=n_triplets,
                            size=(self.max_iter, self.batch_size))

        for iter in range(self.max_iter):
            idx = rand_int[iter]

            slack_val = 1 + np.matmul(dist_diff[idx], w.T)
            slack_mask = np.squeeze(slack_val > 0, axis=1)

            grad_w = np.sum(dist_diff[idx[slack_mask]],
                            axis=0, keepdims=True)/self.batch_size
            avg_grad_w = (iter * avg_grad_w + grad_w) / (iter+1)

            ada_grad_w = np.sqrt(np.square(ada_grad_w) + np.square(grad_w))

            scale_f = -(iter+1) / (self.gamma * (delta + ada_grad_w))

            # proximal operator with negative trimming equivalent
            w = scale_f * np.minimum(avg_grad_w + self.beta, 0)

            if (iter + 1) % self.output_iter == 0:
                # regularization part of obj function
                obj1 = np.sum(w)*self.beta

                # # Every triplet distance difference in the space given by L
                # # plus a slack of one
                # slack_val = 1 + np.matmul(dist_diff, w.T)
                # # Mask of places with positive slack
                # slack_mask = slack_val > 0

                # # loss function of learning task part of obj function
                # obj2 = np.sum(slack_val[slack_mask])/n_triplets

                obj2, count = dist_diff.get_obj2(w.T)
                obj2 = obj2/n_triplets

                obj = obj1 + obj2
                if self.verbose:
                    # count = np.sum(slack_mask)
                    print("[%s] iter %d\t obj %.6f\t num_imp %d" %
                            (self.__class__.__name__, (iter+1), obj, count))

                # update the best
                if obj < best_obj:
                    best_obj = obj
                    best_w = w

        if self.verbose:
            print("max iteration reached.")

        # return L matrix yielded from best weights
        self.n_iter_ = iter
        self.components_ = self._components_from_basis_weights(basis, best_w)

        return self

    def _generate_bases_dist_diff(self, triplets, X):
        """ Constructs the basis set from the differences of positive and negative
        pairs from the triplets constraints.
        The basis set is constructed iteratively by taking n_features triplets,
        then adding and substracting respectively all the outerproducts of the
        positive and negative pairs, and finally selecting the eigenvectors
        of this matrix with positive eigenvalue. This is done until n_basis are
        selected.
        """
        n_features = X.shape[1]
        n_triplets = triplets.shape[0]

        if self.n_basis is None:
            # TODO: Get a good default n_basis directive
            n_basis = n_features*80
            warnings.warn('As no value for `n_basis` was selected, the number of '
                                        'basis will be set to n_basis= %d' % n_basis)
        elif isinstance(self.n_basis, int):
            n_basis = self.n_basis
        else:
            raise ValueError("n_basis should be an integer, instead it is of type %s"
                                             % type(self.n_basis))

        if n_features > n_triplets:
            raise ValueError(
                "Number of features (%s) is greater than the number of triplets(%s).\n"
                "Consider using dimensionality reduction or using another basis "
                "generation scheme." % (n_features, n_triplets))

        basis = np.zeros((n_basis, n_features))

        # get all positive and negative pairs with lowest index first
        # np.array (2*n_triplets,2)
        triplets_pairs_sorted = np.sort(np.vstack((triplets[:, [0, 1]],
                                        triplets[:, [0, 2]])),
                                        kind='stable')

        pos_triplet_pairs = triplets_pairs_sorted[:n_triplets]
        neg_triplet_pairs = triplets_pairs_sorted[n_triplets:]

        # # calculate all unique pairs and their indices
        # uniqPairs, indices = np.unique(triplets_pairs_sorted, 
        #                                return_inverse=True,
        #                                axis=0)
                                       
        # # calculate differences only for unique pairs
        # diff = X[uniqPairs[:, 0], :] - X[uniqPairs[:, 1], :]

        # diff_pos = diff[indices[:n_triplets], :]
        # diff_neg = diff[indices[n_triplets:], :]

        rng = check_random_state(self.random_state)

        start = 0
        finish = 0

        while(finish != n_basis):

            # Select triplets to yield diff

            select_triplet = rng.choice(n_triplets, size=n_features, replace=False)

            # select n_features positive differences
            d_pos = get_dpos(X, pos_triplet_pairs, select_triplet)

            # select n_features negative differences
            d_neg = get_dneg(X, neg_triplet_pairs, select_triplet)

            # Yield matrix
            diff_sum = d_pos.T.dot(d_pos) - d_neg.T.dot(d_neg)

            # Calculate eigenvalue and eigenvectors
            w, v = np.linalg.eigh(diff_sum.T.dot(diff_sum))

            # Add eigenvectors with positive eigenvalue to basis set
            pos_eig_mask = w > 0
            start = finish
            finish += pos_eig_mask.sum()

            try:
                basis[start:finish, :] = v[pos_eig_mask]
            except ValueError:
                # if finish is greater than n_basis
                basis[start:, :] = v[pos_eig_mask][:n_basis-start]
                break

            # TODO: maybe add a warning in case there are no added bases, this could
            # be caused by a bad triplet set. This would cause an infinite loop

        return basis, n_basis


    def _compute_dist_diff(self, triplets, X, basis):
        """
        Helper function to compute the distance difference of every triplet in the
        space yielded by the basis set.
        """
        # Transformation of data by the basis set
        XB = np.matmul(X, basis.T)

        # n_triplets = triplets.shape[0]
        # # get all positive and negative pairs with lowest index first
        # # np.array (2*n_triplets,2)
        # triplets_pairs_sorted = np.sort(np.vstack((triplets[:, [0, 1]],
        #                                            triplets[:, [0, 2]])),
        #                                            kind='stable')

        # # calculate all unique pairs and their indices
        # uniqPairs, indices = np.unique(triplets_pairs_sorted, return_inverse=True,
        #                                                              axis=0)
        # # calculate L2 distance acording to bases only for unique pairs
        # dist = np.square(XB[uniqPairs[:, 0], :] - XB[uniqPairs[:, 1], :])

        # return the difference of distances between all positive and negative
        # pairs
        # return dist[indices[:n_triplets]] - dist[indices[n_triplets:]]
        return CallableArray(XB, triplets)


class CallableArray:

    def __init__(self, XB, triplets):
        self.XB = XB
        self.triplets = triplets
        self.shape = (triplets.shape[0], XB.shape[1])

    def __getitem__(self, index):
        triplet_inds = self.triplets[index]
        dist1 = np.square(self.XB[triplet_inds[:, 0]] - self.XB[triplet_inds[:, 1]])
        dist2 = np.square(self.XB[triplet_inds[:, 0]] - self.XB[triplet_inds[:, 2]])
        return dist1 - dist2

    def get_obj2(self, vector):
        batch_size_est = math.floor(2500000 / self.shape[1])
        batch_size = batch_size_est
        obj2 = 0
        count = 0
        for i in range(0, self.shape[0], batch_size):
            indexes = np.arange(i, min(i+batch_size, self.shape[0]))
            slack_val_i = 1 + np.matmul(self[indexes], vector)
            slack_mask = slack_val_i > 0
            obj2 += np.sum(slack_val_i[slack_mask])
            count += np.sum(slack_mask)
        return (obj2, count)


def get_dpos(X, pos_triplet_pairs, indexes):
    pos_triplets_ind = pos_triplet_pairs[indexes]
    return X[pos_triplets_ind[:, 0]] - X[pos_triplets_ind[:, 1]]


def get_dneg(X, neg_triplet_pairs, indexes):
    neg_triplets_ind = neg_triplet_pairs[indexes]
    return X[neg_triplets_ind[:, 0]] - X[neg_triplets_ind[:, 1]]