import React, { useState, useEffect } from 'react';
import {
  StyleSheet,
  View,
  Text,
  FlatList,
  SafeAreaView,
  ActivityIndicator,
  Image
} from 'react-native';

// THAY IP NÀY BẰNG IP MÁY CHẠY SERVER YOLO
const SERVER_URL = "http://10.136.147.188:5000";
const EVENTS_URL = `${SERVER_URL}/events`;

export default function App() {
  const [events, setEvents] = useState([]);
  const [latestImage, setLatestImage] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  const fetchUpdate = async () => {
    try {
      const response = await fetch(EVENTS_URL);
      const data = await response.json();

      // ✅ Update events (an toàn)
      if (data.events && Array.isArray(data.events)) {
        setEvents([...data.events].reverse());
      }

      // ✅ Update image base64
      if (data.image) {
        setLatestImage(`data:image/jpeg;base64,${data.image}`);
      }

      setIsLoading(false);
    } catch (err) {
      console.error("❌ Lỗi kết nối Server:", err);
    }
  };

  useEffect(() => {
    fetchUpdate();
    const intervalId = setInterval(fetchUpdate, 500); // polling 0.5s
    return () => clearInterval(intervalId);
  }, []);

  return (
    <SafeAreaView style={styles.container}>
      <Text style={styles.title}>YOLOv8 Mobile Monitor 👁️</Text>

      {/* CAMERA VIEW */}
      <View style={styles.cameraBox}>
        {latestImage ? (
          <Image
            source={{ uri: latestImage }}
            style={styles.image}
            resizeMode="cover"
          />
        ) : (
          <View style={styles.loadingBox}>
            <ActivityIndicator size="small" color="#fff" />
            <Text style={styles.loadingText}>
              Connecting to Camera...
            </Text>
          </View>
        )}
      </View>

      {/* EVENT LOG */}
      <View style={styles.logContainer}>
        <Text style={styles.logTitle}>
          Recent Events ({events.length})
        </Text>

        {isLoading ? (
          <ActivityIndicator size="large" color="#0000ff" />
        ) : (
          <FlatList
            data={events}
            keyExtractor={(_, index) => index.toString()}
            renderItem={({ item }) => (
              <View style={styles.eventRow}>
                <Text style={styles.eventText}>• {item}</Text>
              </View>
            )}
            ListEmptyComponent={
              <Text style={styles.empty}>
                No events detected yet.
              </Text>
            }
          />
        )}
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#121212',
    paddingTop: 40
  },
  title: {
    fontSize: 22,
    fontWeight: 'bold',
    color: '#fff',
    textAlign: 'center',
    marginBottom: 15
  },
  cameraBox: {
    width: '94%',
    height: 250,
    backgroundColor: '#000',
    alignSelf: 'center',
    borderRadius: 12,
    overflow: 'hidden',
    borderWidth: 2,
    borderColor: '#333'
  },
  image: {
    width: '100%',
    height: '100%'
  },
  loadingBox: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center'
  },
  loadingText: {
    color: '#fff',
    marginTop: 10
  },
  logContainer: {
    flex: 1,
    backgroundColor: '#fff',
    marginTop: 20,
    borderTopLeftRadius: 25,
    borderTopRightRadius: 25,
    padding: 20
  },
  logTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 10
  },
  eventRow: {
    paddingVertical: 8,
    borderBottomWidth: 0.5,
    borderBottomColor: '#eee'
  },
  eventText: {
    fontSize: 15,
    color: '#444'
  },
  empty: {
    textAlign: 'center',
    marginTop: 20,
    color: '#999'
  }
});
