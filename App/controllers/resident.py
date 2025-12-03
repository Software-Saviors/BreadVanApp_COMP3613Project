from App.models import Resident, Stop, Drive, Area, Street, DriverStock, Driver
from App.database import db

# All resident-related business logic will be moved here as functions

def resident_create(username, password, area_id, street_id, house_number):
    resident = Resident(username=username, password=password, areaId=area_id, streetId=street_id, houseNumber=house_number)
    db.session.add(resident)
    db.session.commit()
    return resident

def resident_request_stop(resident, drive_id):
    drives = Drive.query.filter_by(areaId=resident.areaId, streetId=resident.streetId, status="Upcoming").all()
    if not any(d.id == drive_id for d in drives):
        raise ValueError("Invalid drive choice.")
    existing_stop = Stop.query.filter_by(driveId=drive_id, residentId=resident.id).first()
    if existing_stop:
        raise ValueError(f"You have already requested a stop for drive {drive_id}.")
    return resident.request_stop(drive_id)

def resident_cancel_stop(resident, drive_id):
    stop = Stop.query.filter_by(driveId=drive_id, residentId=resident.id).first()
    if not stop:
        raise ValueError("No stop requested for this drive.")
    resident.cancel_stop(stop.id)
    return stop

def resident_view_inbox(resident):
    return resident.view_inbox()

def resident_view_driver_stats(resident, driver_id):
        driver = Driver.query.get(driver_id)
        if driver:
            return driver.status 
        return None

def resident_view_stock(resident, driver_id):
    driver = resident.view_driver_stats(driver_id)
    if not driver:
         raise ValueError("Driver not found.")
    stocks =  DriverStock.query.filter_by(driverId=driver_id).all()
    return stocks

def resident_subscribe_to_driver(resident, driver_username):
    """
    Subscribe a resident to a driver to receive notifications about their drives.
    """
    driver = Driver.query.filter_by(username=driver_username).first()
    if not driver:
        raise ValueError(f"Driver '{driver_username}' not found.")
    
    # Check if already subscribed
    if driver in resident.subscribed_drivers:
        raise ValueError(f"You are already subscribed to driver '{driver.username}'.")
    
    # Subscribe the resident to the driver
    resident.subscribe_to_driver(driver)
    db.session.commit()
    return driver

def resident_unsubscribe_from_driver(resident, driver_username):
    """
    Unsubscribe a resident from a driver's notifications.
    """
    driver = Driver.query.filter_by(username=driver_username).first()
    if not driver:
        raise ValueError(f"Driver '{driver_username}' not found.")
    
    # Check if subscribed
    if driver not in resident.subscribed_drivers:
        raise ValueError(f"You are not subscribed to driver '{driver.username}'.")
    
    # Unsubscribe the resident from the driver
    resident.unsubscribe_from_driver(driver)
    db.session.commit()
    return driver

def resident_view_subscriptions(resident):
    """
    View all drivers the resident is subscribed to.
    """
    return resident.subscribed_drivers