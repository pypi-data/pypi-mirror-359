#include "VaidyaWalk.hpp"

void VaidyaWalk::setDistTerm(int d, int n){
    DIST_TERM = R*R/(sqrt(d * n));
}

VectorXd VaidyaWalk::generateWeight(const VectorXd& x, const MatrixXd& A, const VectorXd& b){
    VectorXd slack = generateSlack(x, A, b); // sets global slack
    DiagonalMatrix<double, Dynamic> slack_inv = slack.cwiseInverse().asDiagonal();
    MatrixXd half_hess = slack_inv * A; 

    // leverage score computation
    VectorXd wi = (half_hess * (half_hess.transpose() * half_hess).inverse()).cwiseProduct(half_hess).rowwise().sum();

    // leverage score + constants
    wi = wi.array() + (double)A.cols()/A.rows();
    return wi;
}

void VaidyaWalk::printType(){
    cout << "Vaidya Walk" << endl;
}