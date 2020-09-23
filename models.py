from app import db
from datetime import datetime
#from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field

#block tree
class Blocks(db.Model):
    __tablename__ = 'b'

    id = db.Column(db.Integer, primary_key=True)
    timeStamp = db.Column(db.Text, nullable=False)
    data = db.Column(db.Text, nullable=False)
    prevHash = db.Column(db.Text, nullable=False)
    hash = db.Column(db.Text, nullable=False)
    nonce = db.Column(db.Text, nullable=False)

    def __init__(self, *args, **kwargs):
        super(Blocks, self).__init__(*args, **kwargs)
        
    def __repr__(self):
        return 'id: {}, timeStamp: {}, data: {}, prevHash{}, hash: {}, nonce: {}>'.format(self.id, self.timeStamp, self.data, self.prevHash, self.hash, self.nonce)

class Last(db.Model):
    __tablename__ = 'l'

    id = db.Column(db.Integer, primary_key=True)
    last_block_id = db.Column(db.Integer, nullable=False)
    last_block_hash = db.Column(db.Text, nullable=False)

    def __init__(self, *args, **kwargs):
        super(Last, self).__init__(*args, **kwargs)
        
    def __repr__(self):
        return 'id: {}, last_block_id: {}, last_block_hash: {}>'.format(self.id, self.last_block_id, self.last_block_hash)

#chain state
#