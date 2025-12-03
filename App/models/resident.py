from datetime import datetime
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy import JSON

from App.database import db
from .user import User
from .driver import Driver
from .stop import Stop
from .observer import Observer

MAX_INBOX_SIZE = 20

# Association table for the many-to-many relationship between Resident and Driver
driver_subscriptions = db.Table('driver_subscriptions',
    db.Column('resident_id', db.Integer, db.ForeignKey('resident.id'), primary_key=True),
    db.Column('driver_id', db.Integer, db.ForeignKey('driver.id'), primary_key=True)
)


class Resident(User, Observer):
    __tablename__ = "resident"

    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    areaId = db.Column(db.Integer, db.ForeignKey('area.id'), nullable=False)
    streetId = db.Column(db.Integer, db.ForeignKey('street.id'), nullable=False)
    houseNumber = db.Column(db.Integer, nullable=False)
    inbox = db.Column(MutableList.as_mutable(JSON), default=[])

    area = db.relationship("Area", backref='residents')
    street = db.relationship("Street", backref='residents')
    stops = db.relationship('Stop', backref='resident')
    
    # Observer pattern: many-to-many relationship with drivers
    subscribed_drivers = db.relationship('Driver', 
                                        secondary=driver_subscriptions,
                                        backref=db.backref('subscribers', lazy='dynamic'))

    __mapper_args__ = {
        "polymorphic_identity": "Resident",
    }

    def __init__(self, username, password, areaId, streetId, houseNumber):
        super().__init__(username, password)
        self.areaId = areaId
        self.streetId = streetId
        self.houseNumber = houseNumber

    def get_json(self):
        user_json = super().get_json()
        user_json['areaId'] = self.areaId
        user_json['streetId'] = self.streetId
        user_json['houseNumber'] = self.houseNumber
        user_json['inbox'] = self.inbox
        return user_json

    def request_stop(self, driveId):
        try:
            new_stop = Stop(driveId=driveId, residentId=self.id)
            db.session.add(new_stop)
            db.session.commit()
            return new_stop
        except Exception:
            db.session.rollback()
            return None

    def cancel_stop(self, stopId):
        stop = Stop.query.get(stopId)
        if stop:
            db.session.delete(stop)
            db.session.commit()

    def receive_notif(self, message):
        if self.inbox is None:
            self.inbox = []

        if len(self.inbox) >= MAX_INBOX_SIZE:
            self.inbox.pop(0)

        timestamp = datetime.now().strftime("%Y:%m:%d:%H:%M:%S")
        notif = f"[{timestamp}]: {message}"
        self.inbox.append(notif)
        db.session.add(self)
        db.session.commit()

    def view_inbox(self):
        return self.inbox

    def view_driver_stats(self, driverId):
        return Driver.query.get(driverId)

    def update(self, message):
        print(f"[NOTIFY] Resident {self.id}: {message}")
        self.receive_notif(message)
    
    # Observer pattern methods
    def subscribe_to_driver(self, driver):
        """Subscribe to a driver to receive notifications"""
        if driver not in self.subscribed_drivers:
            self.subscribed_drivers.append(driver)
    
    def unsubscribe_from_driver(self, driver):
        """Unsubscribe from a driver's notifications"""
        if driver in self.subscribed_drivers:
            self.subscribed_drivers.remove(driver)