class GPS:
    @staticmethod
    def transform_coordinates(coordinates):
        lat, latDir, lon, lonDir, _, _, _, _, _ = coordinates.split(',')
        
        latDeg = lat[:2]
        latMin = lat[2:]
        lonDeg = lon[:3]
        lonMin = lon[3:]
        
        finalLat = float(latDeg) + (float(latMin)/60)
        finalLon = float(lonDeg) + (float(lonMin)/60)
        if latDir == 'S': finalLat = -finalLat
        if lonDir == 'W': finalLon = -finalLon
        
        return finalLat, finalLon
