class Rating(object):
    """
    Ratings Wrapper

    Provides an composite column interface for SQLAlchemy ORM.
    """

    def __init__(self, sum, votes):
        self.sum = sum
        self.votes = votes

    def __composite_values__(self):
        return [self.sum, self.votes]

    def __eq__(self, other):
        return other.sum == self.sum and other.votes == self.votes

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return '<Rating: %f>' % self.calculate()

    def __unicode__(self):
        return u'%f' % self.calculate()

    def calculate(self):
        if self.votes == 0:
            return 0
        return self.sum / self.votes

    def add_vote(self, voted_rating):
        self.votes += 1
        self.sum   += voted_rating
        return self

class FiveStarRating(Rating):
    def calculate(self):
        rating = super(FiveStarRating, Rating).calculate()
        rounded = round(rating, 1)
        return rounded
