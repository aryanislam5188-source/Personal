import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Animated,
  Dimensions,
  Alert,
  Modal,
  TextInput,
  SafeAreaView,
  ScrollView,
  Platform,
  FlatList
} from 'react-native';
import { StatusBar } from 'expo-status-bar';
import { Ionicons } from '@expo/vector-icons';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { create } from 'zustand';

const { width, height } = Dimensions.get('window');
const EXPO_PUBLIC_BACKEND_URL = process.env.EXPO_PUBLIC_BACKEND_URL;

// Zustand Store for app state
interface AppState {
  userId: string;
  protectionState: 'OFF' | 'BACKGROUND' | 'ACTIVE';
  theme: 'purple' | 'red';
  clickCount: number;
  protectedApps: any[];
  isAuthenticated: boolean;
  password: string;
  setUserId: (id: string) => void;
  setProtectionState: (state: 'OFF' | 'BACKGROUND' | 'ACTIVE') => void;
  setTheme: (theme: 'purple' | 'red') => void;
  incrementClickCount: () => void;
  setProtectedApps: (apps: any[]) => void;
  setAuthenticated: (auth: boolean) => void;
  setPassword: (password: string) => void;
  resetClickCount: () => void;
}

const useAppStore = create<AppState>((set) => ({
  userId: '',
  protectionState: 'OFF',
  theme: 'purple',
  clickCount: 0,
  protectedApps: [],
  isAuthenticated: false,
  password: '',
  setUserId: (id) => set({ userId: id }),
  setProtectionState: (state) => set({ protectionState: state }),
  setTheme: (theme) => set({ theme }),
  incrementClickCount: () => set((state) => ({ clickCount: state.clickCount + 1 })),
  setProtectedApps: (apps) => set({ protectedApps: apps }),
  setAuthenticated: (auth) => set({ isAuthenticated: auth }),
  setPassword: (password) => set({ password }),
  resetClickCount: () => set({ clickCount: 0 })
}));

// Mock popular apps
const MOCK_APPS = [
  { name: 'Facebook', package_name: 'com.facebook.katana', icon: '📘' },
  { name: 'WhatsApp', package_name: 'com.whatsapp', icon: '💬' },
  { name: 'Instagram', package_name: 'com.instagram.android', icon: '📷' },
  { name: 'TikTok', package_name: 'com.zhiliaoapp.musically', icon: '🎵' },
  { name: 'YouTube', package_name: 'com.google.android.youtube', icon: '▶️' },
  { name: 'Twitter', package_name: 'com.twitter.android', icon: '🐦' },
  { name: 'Snapchat', package_name: 'com.snapchat.android', icon: '👻' },
  { name: 'Netflix', package_name: 'com.netflix.mediaclient', icon: '🎬' },
  { name: 'Spotify', package_name: 'com.spotify.music', icon: '🎶' },
  { name: 'Games', package_name: 'com.games.app', icon: '🎮' }
];

export default function PersonalIssueApp() {
  const {
    protectionState,
    theme,
    clickCount,
    protectedApps,
    isAuthenticated,
    password,
    setProtectionState,
    setTheme,
    incrementClickCount,
    setProtectedApps,
    setAuthenticated,
    setPassword,
    resetClickCount
  } = useAppStore();

  // Animation values
  const [backgroundColorAnim] = useState(new Animated.Value(0));
  const [scaleAnim] = useState(new Animated.Value(1));

  // Modal states
  const [showPasswordModal, setShowPasswordModal] = useState(false);
  const [showAppSelector, setShowAppSelector] = useState(false);
  const [showUnlockModal, setShowUnlockModal] = useState(false);
  const [showSettings, setShowSettings] = useState(false);

  // Form states
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [unlockPassword, setUnlockPassword] = useState('');

  // Load saved data
  useEffect(() => {
    loadSavedData();
  }, []);

  // Animate theme change
  useEffect(() => {
    Animated.timing(backgroundColorAnim, {
      toValue: theme === 'red' ? 1 : 0,
      duration: 500,
      useNativeDriver: false
    }).start();
  }, [theme]);

  const loadSavedData = async () => {
    try {
      const savedState = await AsyncStorage.getItem('personalIssueState');
      if (savedState) {
        const state = JSON.parse(savedState);
        setProtectionState(state.protectionState || 'OFF');
        setTheme(state.theme || 'purple');
        setProtectedApps(state.protectedApps || []);
        setPassword(state.password || '');
      }
    } catch (error) {
      console.log('Error loading saved data:', error);
    }
  };

  const saveState = async () => {
    try {
      const state = {
        protectionState,
        theme,
        protectedApps,
        password
      };
      await AsyncStorage.setItem('personalIssueState', JSON.stringify(state));
    } catch (error) {
      console.log('Error saving state:', error);
    }
  };

  // Handle app clicks (3-click system)
  const handleAppClick = () => {
    const newClickCount = clickCount + 1;
    incrementClickCount();
    
    if (newClickCount === 1) {
      // First click - Setup mode (already in setup by default)
      console.log('First click - Setup mode');
    } else if (newClickCount === 2) {
      // Second click - Background protection mode
      if (!password) {
        setShowPasswordModal(true);
      } else {
        handleToggleProtection();
      }
    } else if (newClickCount === 3) {
      // Third click - Full protection active
      setProtectionState('ACTIVE');
      setTheme('red');
      saveState();
      Alert.alert(
        'Protection Active!',
        'Your protected apps are now frozen. Use your password to unlock them.',
        [{ text: 'OK' }]
      );
    }
  };

  const handleToggleProtection = () => {
    if (protectionState === 'OFF') {
      setProtectionState('BACKGROUND');
      setTheme('red');
      // Auto-minimize simulation
      setTimeout(() => {
        Alert.alert(
          'Protection ON',
          'App is now running in background mode. Open again to activate full protection.',
          [{ text: 'OK' }]
        );
      }, 1000);
    } else {
      setProtectionState('OFF');
      setTheme('purple');
      resetClickCount();
    }
    saveState();
  };

  const handlePasswordSetup = () => {
    if (newPassword.length > 8) {
      Alert.alert('Error', 'Password must be 8 characters or less.');
      return;
    }
    if (newPassword !== confirmPassword) {
      Alert.alert('Error', 'Passwords do not match.');
      return;
    }
    if (newPassword.length === 0) {
      Alert.alert('Error', 'Password cannot be empty.');
      return;
    }

    setPassword(newPassword);
    setShowPasswordModal(false);
    setNewPassword('');
    setConfirmPassword('');
    handleToggleProtection();
  };

  const handleUnlock = () => {
    if (unlockPassword === password) {
      setShowUnlockModal(false);
      setUnlockPassword('');
      Alert.alert(
        'Choose Action',
        'What would you like to do?',
        [
          {
            text: 'Turn OFF Protection',
            onPress: () => {
              setProtectionState('OFF');
              setTheme('purple');
              resetClickCount();
              saveState();
            }
          },
          {
            text: 'Temporarily Allow Apps',
            onPress: () => {
              Alert.alert('Success', 'Protected apps temporarily unlocked for 5 minutes.');
            }
          },
          { text: 'Cancel', style: 'cancel' }
        ]
      );
    } else {
      Alert.alert('Error', 'Incorrect password.');
    }
  };

  const addProtectedApp = (app: any) => {
    if (protectedApps.length >= 20) {
      Alert.alert('Error', 'Maximum 20 apps allowed.');
      return;
    }
    if (protectedApps.find(a => a.package_name === app.package_name)) {
      Alert.alert('Error', 'App already added.');
      return;
    }
    setProtectedApps([...protectedApps, app]);
    saveState();
  };

  const removeProtectedApp = (packageName: string) => {
    setProtectedApps(protectedApps.filter(app => app.package_name !== packageName));
    saveState();
  };

  const handleProtectedAppClick = (app: any) => {
    if (protectionState === 'ACTIVE') {
      // Simulate frozen app behavior
      Animated.sequence([
        Animated.timing(scaleAnim, { toValue: 0.95, duration: 100, useNativeDriver: true }),
        Animated.timing(scaleAnim, { toValue: 1, duration: 100, useNativeDriver: true })
      ]).start();
      
      setTimeout(() => {
        Alert.alert(
          '🔒 App Frozen',
          `${app.name} is protected. Enter password to unlock.`,
          [
            { text: 'Cancel', style: 'cancel' },
            { text: 'Unlock', onPress: () => setShowUnlockModal(true) }
          ]
        );
      }, 200);
    } else {
      Alert.alert('App Simulation', `${app.name} would open normally (protection not active).`);
    }
  };

  const backgroundColor = backgroundColorAnim.interpolate({
    inputRange: [0, 1],
    outputRange: ['#7A5CFF', '#FF4C4C']
  });

  const renderAppSlot = ({ item, index }: { item: any, index: number }) => {
    if (item.isEmpty) {
      return (
        <TouchableOpacity
          style={[styles.appSlot, styles.emptySlot]}
          onPress={() => setShowAppSelector(true)}
        >
          <Ionicons name="add" size={32} color={theme === 'red' ? '#FF4C4C' : '#7A5CFF'} />
        </TouchableOpacity>
      );
    }

    return (
      <Animated.View style={{ transform: [{ scale: scaleAnim }] }}>
        <TouchableOpacity
          style={[styles.appSlot, styles.filledSlot]}
          onPress={() => handleProtectedAppClick(item)}
        >
          <Text style={styles.appIcon}>{item.icon}</Text>
          <Text style={styles.appName} numberOfLines={1}>{item.name}</Text>
          <TouchableOpacity
            style={styles.removeButton}
            onPress={() => removeProtectedApp(item.package_name)}
          >
            <Ionicons name="close-circle" size={20} color="#FF3333" />
          </TouchableOpacity>
        </TouchableOpacity>
      </Animated.View>
    );
  };

  const getGridData = () => {
    const data = [...protectedApps];
    while (data.length < 10) {
      data.push({ isEmpty: true, id: `empty-${data.length}` });
    }
    return data;
  };

  const renderGrid = () => {
    const gridData = getGridData();
    const rows = [];
    for (let i = 0; i < gridData.length; i += 5) {
      const rowData = gridData.slice(i, i + 5);
      rows.push(
        <View key={i} style={styles.gridRow}>
          {rowData.map((item, index) => (
            <View key={item.package_name || item.id || `${i}-${index}`}>
              {renderAppSlot({ item, index: i + index })}
            </View>
          ))}
        </View>
      );
    }
    return (
      <View>
        {rows}
      </View>
    );
  };

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar style={theme === 'red' ? 'light' : 'dark'} />
      
      <Animated.View style={[styles.container, { backgroundColor }]}>
        {/* Header */}
        <View style={styles.header}>
          <View style={styles.headerLeft}>
            <Text style={styles.appTitle}>Personal Issue</Text>
            <Text style={styles.logoSubtext}>Logo</Text>
          </View>
          <TouchableOpacity style={styles.accountButton}>
            <Ionicons name="person-circle-outline" size={28} color="#333" />
            <Text style={styles.accountText}>MY Account</Text>
          </TouchableOpacity>
        </View>

        {/* ON/OFF Toggle */}
        <View style={styles.toggleContainer}>
          <TouchableOpacity
            style={[
              styles.toggleButton,
              protectionState !== 'OFF' ? styles.toggleActive : styles.toggleInactive
            ]}
            onPress={handleAppClick}
          >
            <Text style={[
              styles.toggleText,
              protectionState !== 'OFF' ? styles.toggleTextActive : styles.toggleTextInactive
            ]}>ON</Text>
          </TouchableOpacity>
          
          <TouchableOpacity
            style={[
              styles.toggleButton,
              protectionState === 'OFF' ? styles.toggleActive : styles.toggleInactive
            ]}
            onPress={() => {
              setProtectionState('OFF');
              setTheme('purple');
              resetClickCount();
              saveState();
            }}
          >
            <Text style={[
              styles.toggleText,
              protectionState === 'OFF' ? styles.toggleTextActive : styles.toggleTextInactive
            ]}>OFF</Text>
          </TouchableOpacity>
        </View>

        {/* Apps Grid */}
        <View style={styles.gridContainer}>
          <ScrollView 
            style={styles.grid}
            contentContainerStyle={styles.gridContent}
            scrollEnabled={false}
          >
            {renderGrid()}
          </ScrollView>
          
          {protectedApps.length >= 10 && (
            <TouchableOpacity style={styles.addMoreButton}>
              <Text style={styles.addMoreText}>Add More</Text>
            </TouchableOpacity>
          )}
        </View>

        {/* Bottom Controls */}
        <View style={styles.bottomControls}>
          <TouchableOpacity 
            style={styles.bottomButton}
            onPress={() => setShowSettings(true)}
          >
            <Ionicons name="settings-outline" size={24} color="#333" />
            <Text style={styles.bottomButtonText}>Settings</Text>
          </TouchableOpacity>
          
          <TouchableOpacity 
            style={styles.bottomButton}
            onPress={() => {
              if (password) {
                Alert.alert('Password Check', `Your password is: ${password}`);
              } else {
                Alert.alert('No Password', 'No password has been set yet.');
              }
            }}
          >
            <Ionicons name="lock-closed-outline" size={24} color="#333" />
            <Text style={styles.bottomButtonText}>Check My Pass</Text>
          </TouchableOpacity>
        </View>

        {/* Password Setup Modal */}
        <Modal visible={showPasswordModal} transparent animationType="fade">
          <View style={styles.modalOverlay}>
            <View style={styles.modalContainer}>
              <Text style={styles.modalTitle}>Create Password</Text>
              <Text style={styles.modalSubtitle}>Max 8 characters</Text>
              
              <TextInput
                style={styles.modalInput}
                placeholder="Enter password"
                value={newPassword}
                onChangeText={setNewPassword}
                secureTextEntry
                maxLength={8}
              />
              
              <TextInput
                style={styles.modalInput}
                placeholder="Confirm password"
                value={confirmPassword}
                onChangeText={setConfirmPassword}
                secureTextEntry
                maxLength={8}
              />
              
              <View style={styles.modalButtons}>
                <TouchableOpacity
                  style={[styles.modalButton, styles.cancelButton]}
                  onPress={() => {
                    setShowPasswordModal(false);
                    setNewPassword('');
                    setConfirmPassword('');
                  }}
                >
                  <Text style={styles.cancelButtonText}>Cancel</Text>
                </TouchableOpacity>
                
                <TouchableOpacity
                  style={[styles.modalButton, styles.confirmButton]}
                  onPress={handlePasswordSetup}
                >
                  <Text style={styles.confirmButtonText}>Create</Text>
                </TouchableOpacity>
              </View>
            </View>
          </View>
        </Modal>

        {/* App Selector Modal */}
        <Modal visible={showAppSelector} transparent animationType="slide">
          <View style={styles.modalOverlay}>
            <View style={[styles.modalContainer, styles.appSelectorModal]}>
              <Text style={styles.modalTitle}>Select Apps to Protect</Text>
              
              <ScrollView style={styles.appList}>
                {MOCK_APPS.map(app => (
                  <TouchableOpacity
                    key={app.package_name}
                    style={styles.appListItem}
                    onPress={() => {
                      addProtectedApp(app);
                      setShowAppSelector(false);
                    }}
                  >
                    <Text style={styles.appListIcon}>{app.icon}</Text>
                    <Text style={styles.appListName}>{app.name}</Text>
                  </TouchableOpacity>
                ))}
              </ScrollView>
              
              <TouchableOpacity
                style={[styles.modalButton, styles.cancelButton, { width: '100%' }]}
                onPress={() => setShowAppSelector(false)}
              >
                <Text style={styles.cancelButtonText}>Close</Text>
              </TouchableOpacity>
            </View>
          </View>
        </Modal>

        {/* Unlock Modal */}
        <Modal visible={showUnlockModal} transparent animationType="fade">
          <View style={styles.modalOverlay}>
            <View style={styles.modalContainer}>
              <Text style={styles.modalTitle}>Enter Password</Text>
              
              <TextInput
                style={styles.modalInput}
                placeholder="Enter your password"
                value={unlockPassword}
                onChangeText={setUnlockPassword}
                secureTextEntry
                maxLength={8}
              />
              
              <View style={styles.modalButtons}>
                <TouchableOpacity
                  style={[styles.modalButton, styles.cancelButton]}
                  onPress={() => {
                    setShowUnlockModal(false);
                    setUnlockPassword('');
                  }}
                >
                  <Text style={styles.cancelButtonText}>Cancel</Text>
                </TouchableOpacity>
                
                <TouchableOpacity
                  style={[styles.modalButton, styles.confirmButton]}
                  onPress={handleUnlock}
                >
                  <Text style={styles.confirmButtonText}>Unlock</Text>
                </TouchableOpacity>
              </View>
            </View>
          </View>
        </Modal>
      </Animated.View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingTop: 20,
    paddingBottom: 10
  },
  headerLeft: {
    alignItems: 'center'
  },
  appTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333'
  },
  logoSubtext: {
    fontSize: 14,
    color: '#666',
    marginTop: 4
  },
  accountButton: {
    alignItems: 'center'
  },
  accountText: {
    fontSize: 12,
    color: '#333',
    marginTop: 4
  },
  toggleContainer: {
    flexDirection: 'row',
    justifyContent: 'center',
    marginVertical: 30,
    paddingHorizontal: 20
  },
  toggleButton: {
    paddingVertical: 15,
    paddingHorizontal: 40,
    marginHorizontal: 10,
    borderRadius: 25,
    minWidth: 80
  },
  toggleActive: {
    backgroundColor: 'rgba(255, 255, 255, 0.9)'
  },
  toggleInactive: {
    backgroundColor: 'rgba(255, 255, 255, 0.3)'
  },
  toggleText: {
    fontSize: 18,
    fontWeight: 'bold',
    textAlign: 'center'
  },
  toggleTextActive: {
    color: '#333'
  },
  toggleTextInactive: {
    color: 'rgba(255, 255, 255, 0.7)'
  },
  gridContainer: {
    flex: 1,
    paddingHorizontal: 20,
    alignItems: 'center'
  },
  grid: {
    width: '100%',
    maxHeight: 200
  },
  gridRow: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    paddingHorizontal: 10
  },
  gridContent: {
    paddingVertical: 10
  },
  appSlot: {
    width: 60,
    height: 80,
    alignItems: 'center',
    justifyContent: 'center',
    borderRadius: 15,
    position: 'relative'
  },
  emptySlot: {
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
    borderWidth: 2,
    borderColor: 'rgba(255, 255, 255, 0.4)',
    borderStyle: 'dashed'
  },
  filledSlot: {
    backgroundColor: 'rgba(255, 255, 255, 0.9)'
  },
  appIcon: {
    fontSize: 28,
    marginBottom: 4
  },
  appName: {
    fontSize: 10,
    color: '#333',
    textAlign: 'center'
  },
  removeButton: {
    position: 'absolute',
    top: -5,
    right: -5,
    backgroundColor: 'white',
    borderRadius: 10,
    width: 20,
    height: 20,
    alignItems: 'center',
    justifyContent: 'center'
  },
  addMoreButton: {
    marginTop: 20,
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
    paddingVertical: 10,
    paddingHorizontal: 20,
    borderRadius: 15,
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.4)'
  },
  addMoreText: {
    color: 'white',
    fontWeight: '600'
  },
  bottomControls: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingHorizontal: 20,
    paddingVertical: 20,
    paddingBottom: Platform.OS === 'ios' ? 40 : 20
  },
  bottomButton: {
    alignItems: 'center',
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
    paddingVertical: 15,
    paddingHorizontal: 20,
    borderRadius: 15,
    minWidth: 100
  },
  bottomButtonText: {
    color: '#333',
    fontSize: 12,
    marginTop: 5,
    textAlign: 'center',
    fontWeight: '600'
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20
  },
  modalContainer: {
    backgroundColor: 'white',
    borderRadius: 20,
    padding: 20,
    width: '90%',
    maxWidth: 400
  },
  modalTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: 10,
    color: '#333'
  },
  modalSubtitle: {
    fontSize: 14,
    textAlign: 'center',
    color: '#666',
    marginBottom: 20
  },
  modalInput: {
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 10,
    padding: 15,
    marginBottom: 15,
    fontSize: 16
  },
  modalButtons: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 10
  },
  modalButton: {
    flex: 1,
    paddingVertical: 15,
    borderRadius: 10,
    marginHorizontal: 5
  },
  cancelButton: {
    backgroundColor: '#f0f0f0'
  },
  cancelButtonText: {
    color: '#666',
    fontWeight: '600',
    textAlign: 'center'
  },
  confirmButton: {
    backgroundColor: '#007AFF'
  },
  confirmButtonText: {
    color: 'white',
    fontWeight: '600',
    textAlign: 'center'
  },
  appSelectorModal: {
    maxHeight: '80%'
  },
  appList: {
    maxHeight: 300,
    marginBottom: 20
  },
  appListItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 12,
    paddingHorizontal: 10,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0'
  },
  appListIcon: {
    fontSize: 24,
    marginRight: 15
  },
  appListName: {
    fontSize: 16,
    color: '#333'
  }
});