import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'dart:io' show Platform;
import 'dart:async';
import 'package:intl/intl.dart';
import 'package:fl_chart/fl_chart.dart';
import 'package:shared_preferences/shared_preferences.dart';

void main() {
  runApp(const GammaCalculatorApp());
}

class GammaCalculatorApp extends StatelessWidget {
  const GammaCalculatorApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Peace map',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(
          seedColor: Colors.teal,
          brightness: Brightness.dark,
        ),
        useMaterial3: true,
        inputDecorationTheme: const InputDecorationTheme(
          border: OutlineInputBorder(),
          filled: true,
        ),
      ),
      home: const GammaScreen(),
    );
  }
}

class GammaScreen extends StatefulWidget {
  const GammaScreen({super.key});

  @override
  State<GammaScreen> createState() => _GammaScreenState();
}

class _GammaScreenState extends State<GammaScreen>
    with SingleTickerProviderStateMixin {
  final TextEditingController _tickerController = TextEditingController();
  String? _selectedDate;
  List<String> _dates = [];
  bool _isLoadingDates = false;
  bool _isLoadingProfile = false;
  Map<String, dynamic>? _profileData;
  String? _errorMessage;

  // Auto-Refresh
  bool _autoRefresh = false;
  Timer? _refreshTimer;
  DateTime? _lastUpdated;
  final TextEditingController _intervalController = TextEditingController(
    text: "1440",
  );

  // Server Settings
  String _customIp =
      "https://unplenteous-gracelyn-nonoligarchical.ngrok-free.dev";
  String _dataSource = "yahoo"; // 'yahoo' or 'webull'

  // Chart Mode
  int _chartMode = 0; // 0: Net GEX, 1: Split GEX, 2: Open Interest

  String get _baseUrl {
    if (_customIp.isNotEmpty) {
      if (_customIp.startsWith("http")) return _customIp;
      return 'http://$_customIp:5000';
    }
    if (Platform.isAndroid) {
      return 'http://10.0.2.2:5000';
    } else {
      return 'http://127.0.0.1:5000';
    }
  }

  @override
  void initState() {
    super.initState();
    _loadSettings();
  }

  Future<void> _loadSettings() async {
    final prefs = await SharedPreferences.getInstance();
    setState(() {
      // Preserve hardcoded URL if not set in prefs
      String? savedIp = prefs.getString('custom_ip');
      if (savedIp != null) {
        _customIp = savedIp;
      }
      _dataSource = prefs.getString('data_source') ?? "yahoo";
    });
    // Sync with server on load
    if (_dataSource == 'webull') {
      _setDataSource('webull');
    }
  }

  Future<void> _saveSettings(String ip) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('custom_ip', ip);
    setState(() {
      _customIp = ip;
    });
  }

  Future<void> _setDataSource(String source) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('data_source', source);
    setState(() {
      _dataSource = source;
    });

    // Notify Server
    try {
      await http.post(
        Uri.parse('$_baseUrl/api/settings/source'),
        headers: {
          'Content-Type': 'application/json',
          'ngrok-skip-browser-warning': 'true',
        },
        body: json.encode({'source': source}),
      );
    } catch (e) {
      print("Failed to set source on server: $e");
    }
  }

  Future<void> _webullLogin(
    String email,
    String password, {
    String? mfa,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$_baseUrl/api/webull/login'),
        headers: {
          'Content-Type': 'application/json',
          'ngrok-skip-browser-warning': 'true',
        },
        body: json.encode({'email': email, 'password': password, 'mfa': mfa}),
      );
      final data = json.decode(response.body);
      if (data['success'] == true) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Webull Login Successful!')),
        );
        Navigator.pop(context); // Close dialog
      } else if (data['mfa_required'] == true) {
        // Ask for MFA
        Navigator.pop(context);
        _showWebullLoginDialog(email: email, password: password, isMfa: true);
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Login Failed: ${data['error']}')),
        );
      }
    } catch (e) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text('Login Error: $e')));
    }
  }

  void _showSettingsDialog() {
    final TextEditingController ipController = TextEditingController(
      text: _customIp,
    );
    showDialog(
      context: context,
      builder: (context) {
        return AlertDialog(
          title: const Text("Server Connection"),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Text("Enter Server Link (Ngrok) or PC IP:"),
              TextField(
                controller: ipController,
                decoration: const InputDecoration(
                  hintText: "https://... or 192.168.x.x",
                ),
              ),
              const SizedBox(height: 20),
              const Text("Data Source:"),
              Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  ChoiceChip(
                    label: const Text("Yahoo (Delayed)"),
                    selected: _dataSource == 'yahoo',
                    onSelected: (bool selected) {
                      if (selected) _setDataSource('yahoo');
                    },
                  ),
                  const SizedBox(width: 10),
                  ChoiceChip(
                    label: const Text("Webull (Real-time)"),
                    selected: _dataSource == 'webull',
                    onSelected: (bool selected) {
                      if (selected) {
                        _setDataSource('webull');
                        // Prompt login if needed (server check ideally, but force login dialog for now)
                        // check server status first?
                        // For simplicity, show login button in dialog
                      }
                    },
                  ),
                ],
              ),
              if (_dataSource == 'webull')
                Padding(
                  padding: const EdgeInsets.only(top: 10),
                  child: ElevatedButton(
                    onPressed: () {
                      Navigator.pop(context); // Close settings
                      _showWebullLoginDialog();
                    },
                    child: const Text("Webull Login"),
                  ),
                ),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () {
                _saveSettings(""); // Reset
                Navigator.pop(context);
              },
              child: const Text("Reset Default"),
            ),
            ElevatedButton(
              onPressed: () {
                _saveSettings(ipController.text.trim());
                Navigator.pop(context);
              },
              child: const Text("Save"),
            ),
          ],
        );
      },
    );
  }

  void _showWebullLoginDialog({
    String? email,
    String? password,
    bool isMfa = false,
  }) {
    final TextEditingController emailController = TextEditingController(
      text: email ?? "",
    );
    final TextEditingController passwordController = TextEditingController(
      text: password ?? "",
    );
    final TextEditingController mfaController = TextEditingController();

    showDialog(
      context: context,
      builder: (context) {
        return AlertDialog(
          title: Text(isMfa ? "Webull MFA" : "Webull Login"),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              if (!isMfa) ...[
                TextField(
                  controller: emailController,
                  decoration: const InputDecoration(labelText: "Email"),
                ),
                const SizedBox(height: 10),
                TextField(
                  controller: passwordController,
                  decoration: const InputDecoration(labelText: "Password"),
                  obscureText: true,
                ),
              ],
              if (isMfa)
                TextField(
                  controller: mfaController,
                  decoration: const InputDecoration(
                    labelText: "MFA Code (SMS/App)",
                  ),
                ),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text("Cancel"),
            ),
            ElevatedButton(
              onPressed: () {
                if (isMfa) {
                  _webullLogin(email!, password!, mfa: mfaController.text);
                } else {
                  _webullLogin(emailController.text, passwordController.text);
                }
              },
              child: const Text("Login"),
            ),
          ],
        );
      },
    );
  }

  @override
  void dispose() {
    _refreshTimer?.cancel();
    _tickerController.dispose();
    _intervalController.dispose();
    super.dispose();
  }

  void _toggleAutoRefresh(bool value) {
    setState(() {
      _autoRefresh = value;
    });
    _startTimer();
  }

  void _startTimer() {
    _refreshTimer?.cancel();
    if (_autoRefresh) {
      int seconds = int.tryParse(_intervalController.text) ?? 1;
      if (seconds < 1) seconds = 1;
      if (seconds > 999) seconds = 999;

      _refreshTimer = Timer.periodic(Duration(seconds: seconds), (timer) {
        if (_selectedDate != null && !_isLoadingProfile) {
          _fetchProfile(isAuto: true);
        }
      });
    }
  }

  Future<void> _fetchDates() async {
    final ticker = _tickerController.text.toUpperCase().trim();
    if (ticker.isEmpty) return;

    setState(() {
      _isLoadingDates = true;
      _errorMessage = null;
      _dates = [];
      _selectedDate = null;
      _profileData = null;
      _lastUpdated = null;
    });

    try {
      final response = await http.get(
        Uri.parse('$_baseUrl/dates?ticker=$ticker'),
        headers: {'ngrok-skip-browser-warning': 'true'},
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        setState(() {
          _dates = List<String>.from(data['dates']);
          if (_dates.isNotEmpty) {
            _selectedDate = _dates.first;
          }
        });
      } else {
        setState(() {
          _errorMessage = "Failed to fetch dates";
        });
      }
    } catch (e) {
      setState(() {
        _errorMessage = "Connection error: $e";
      });
    } finally {
      setState(() {
        _isLoadingDates = false;
      });
    }
  }

  Future<void> _fetchProfile({bool isAuto = false}) async {
    final ticker = _tickerController.text.toUpperCase().trim();

    if (ticker.isEmpty || _selectedDate == null) return;

    if (!isAuto) {
      setState(() {
        _isLoadingProfile = true;
        _errorMessage = null;
      });
    }

    try {
      final url = '$_baseUrl/profile?ticker=$ticker&date=$_selectedDate';
      final response = await http.get(
        Uri.parse(url),
        headers: {'ngrok-skip-browser-warning': 'true'},
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        setState(() {
          _profileData = data;
          _lastUpdated = DateTime.now();
        });
      } else {
        if (!isAuto) {
          setState(() {
            _errorMessage = "Failed to fetch profile";
          });
        }
      }
    } catch (e) {
      if (!isAuto) {
        setState(() {
          _errorMessage = "Connection error: $e";
        });
      }
    } finally {
      setState(() {
        _isLoadingProfile = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Peace map'),
        centerTitle: true,
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
        actions: [
          IconButton(
            icon: const Icon(Icons.settings),
            onPressed: _showSettingsDialog,
          ),
          if (_lastUpdated != null)
            Center(
              child: Padding(
                padding: const EdgeInsets.only(right: 16.0),
                child: Text(
                  DateFormat('HH:mm').format(_lastUpdated!),
                  style: const TextStyle(fontSize: 12, color: Colors.white70),
                ),
              ),
            ),
        ],
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              _buildSetupCard(),
              const SizedBox(height: 10),
              if (_errorMessage != null)
                Text(_errorMessage!, style: const TextStyle(color: Colors.red)),
              if (_profileData != null) _buildProfileView(),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildSetupCard() {
    return Card(
      elevation: 4,
      child: Padding(
        padding: const EdgeInsets.all(12.0),
        child: Column(
          children: [
            Row(
              children: [
                Expanded(
                  child: Autocomplete<String>(
                    optionsBuilder: (TextEditingValue textEditingValue) async {
                      if (textEditingValue.text.length < 2) {
                        return const Iterable<String>.empty();
                      }
                      try {
                        final url =
                            '$_baseUrl/search?q=${textEditingValue.text}';
                        final response = await http.get(
                          Uri.parse(url),
                          headers: {'ngrok-skip-browser-warning': 'true'},
                        );
                        if (response.statusCode == 200) {
                          final data = json.decode(response.body);
                          final results = data['results'] as List;
                          return results.map((e) => e['symbol'].toString());
                        }
                      } catch (e) {
                        print("Search error: $e");
                      }
                      return const Iterable<String>.empty();
                    },
                    onSelected: (String selection) {
                      _tickerController.text = selection;
                      _fetchDates();
                    },
                    fieldViewBuilder:
                        (
                          context,
                          textEditingController,
                          focusNode,
                          onFieldSubmitted,
                        ) {
                          // Sync external controller if needed, but for now just use the one provided
                          // Or listen to changes. Simple way: user types here.
                          // We must keep _tickerController in sync or use this controller.
                          _tickerController.text = textEditingController.text;
                          textEditingController.addListener(() {
                            _tickerController.text = textEditingController.text;
                          });

                          return TextField(
                            controller: textEditingController,
                            focusNode: focusNode,
                            onSubmitted: (val) {
                              _tickerController.text = val;
                              _fetchDates();
                            },
                            decoration: const InputDecoration(
                              labelText: 'Search Company or Ticker',
                              isDense: true,
                              suffixIcon: Icon(Icons.search),
                            ),
                          );
                        },
                  ),
                ),
                const SizedBox(width: 8),
                IconButton.filledTonal(
                  onPressed: _fetchDates,
                  icon: const Icon(Icons.search),
                ),
              ],
            ),
            const SizedBox(height: 10),
            const SizedBox(height: 10),
            const SizedBox(height: 10),
            if (_dates.isNotEmpty)
              DropdownButtonFormField<String>(
                decoration: const InputDecoration(
                  labelText: 'Expiration',
                  isDense: true,
                ),
                value: _selectedDate,
                items: _dates
                    .map(
                      (date) =>
                          DropdownMenuItem(value: date, child: Text(date)),
                    )
                    .toList(),
                onChanged: (val) {
                  setState(() {
                    _selectedDate = val;
                  });
                  // Auto fetch when date changes
                  Future.delayed(Duration.zero, _fetchProfile);
                },
              ),
            const SizedBox(height: 10),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Row(
                  children: [
                    Switch(value: _autoRefresh, onChanged: _toggleAutoRefresh),
                    const Text("Auto: "),
                    SizedBox(
                      width: 60,
                      child: TextField(
                        controller: _intervalController,
                        keyboardType: TextInputType.number,
                        textAlign: TextAlign.center,
                        decoration: const InputDecoration(
                          isDense: true,
                          contentPadding: EdgeInsets.symmetric(vertical: 8),
                        ),
                        onChanged: (val) {
                          if (_autoRefresh) _startTimer();
                        },
                      ),
                    ),
                    const Text("s"),
                  ],
                ),
                ElevatedButton(
                  onPressed: _isLoadingProfile ? null : _fetchProfile,
                  child: _isLoadingProfile
                      ? const Text("Loading...")
                      : const Text("Refresh Now"),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildProfileView() {
    final spot = (_profileData!['spot_price'] as num).toDouble();
    final List<dynamic> profile = _profileData!['profile'];

    if (profile.isEmpty) {
      return const Center(
        child: Padding(
          padding: EdgeInsets.all(20.0),
          child: Text(
            "No Gamma Data Available for this expiration.",
            style: TextStyle(color: Colors.white70),
          ),
        ),
      );
    }

    // Filter logic: Find spot, take +/- range
    int nearestIndex = 0;
    double minDiff = double.infinity;
    for (int i = 0; i < profile.length; i++) {
      final strike = (profile[i]['strike'] as num).toDouble();
      final diff = (strike - spot).abs();
      if (diff < minDiff) {
        minDiff = diff;
        nearestIndex = i;
      }
    }
    int start = (nearestIndex - 12).clamp(0, profile.length);
    int end = (nearestIndex + 12).clamp(0, profile.length);
    final chartData = profile.sublist(start, end);

    // Identify Support (Max Negative GEX) and Resistance (Max Positive GEX)
    double maxPosGex = -double.infinity;
    double maxNegGex = double.infinity;
    int? resistanceIndex;
    int? supportIndex;

    for (int i = 0; i < chartData.length; i++) {
      final net = (chartData[i]['net_gex'] as num).toDouble();
      if (net > maxPosGex) {
        maxPosGex = net;
        resistanceIndex = i;
      }
      if (net < maxNegGex) {
        maxNegGex = net;
        supportIndex = i;
      }
    }

    print("DEBUG: Resistance Index: $resistanceIndex (Gex: $maxPosGex)");
    print("DEBUG: Support Index: $supportIndex (Gex: $maxNegGex)");

    // Identify Top 5 Call OI and Top 5 Put OI indices in the visible range
    final List<MapEntry<int, double>> callOis = [];
    final List<MapEntry<int, double>> putOis = [];

    for (int i = 0; i < chartData.length; i++) {
      final item = chartData[i];
      final call = (item['call_oi'] ?? 0 as num).toDouble();
      final put = (item['put_oi'] ?? 0 as num).toDouble();
      callOis.add(MapEntry(i, call));
      putOis.add(MapEntry(i, put));
    }

    callOis.sort((a, b) => b.value.compareTo(a.value));
    putOis.sort((a, b) => b.value.compareTo(a.value));

    final Set<int> topCallIndices = callOis.take(5).map((e) => e.key).toSet();
    final Set<int> topPutIndices = putOis.take(5).map((e) => e.key).toSet();

    // Identify Top 3 Call GEX and Top 3 Put GEX indices for Absolute Gamma mode
    final List<MapEntry<int, double>> callGexList = [];
    final List<MapEntry<int, double>> putGexList = [];

    for (int i = 0; i < chartData.length; i++) {
      final item = chartData[i];
      final callG = (item['call_gex'] as num).toDouble();
      final putG = (item['put_gex'] as num).toDouble();
      callGexList.add(MapEntry(i, callG));
      putGexList.add(MapEntry(i, putG.abs())); // compare magnitude
    }

    callGexList.sort((a, b) => b.value.compareTo(a.value));
    putGexList.sort((a, b) => b.value.compareTo(a.value));

    final Set<int> topCallGexIndices = callGexList
        .take(5)
        .map((e) => e.key)
        .toSet();
    final Set<int> topPutGexIndices = putGexList
        .take(5)
        .map((e) => e.key)
        .toSet();
    final Set<int> topGexIndices = {...topCallGexIndices, ...topPutGexIndices};

    // Identify Top 5 Call Vol and Top 5 Put Vol indices for Top Volume mode
    final List<MapEntry<int, double>> callVolList = [];
    final List<MapEntry<int, double>> putVolList = [];

    for (int i = 0; i < chartData.length; i++) {
      final item = chartData[i];
      final cVol = (item['call_vol'] ?? 0 as num).toDouble();
      final pVol = (item['put_vol'] ?? 0 as num).toDouble();
      callVolList.add(MapEntry(i, cVol));
      putVolList.add(MapEntry(i, pVol));
    }

    callVolList.sort((a, b) => b.value.compareTo(a.value));
    putVolList.sort((a, b) => b.value.compareTo(a.value));

    final Set<int> topCallVolIndices = callVolList
        .take(5)
        .map((e) => e.key)
        .toSet();
    final Set<int> topPutVolIndices = putVolList
        .take(5)
        .map((e) => e.key)
        .toSet();
    final Set<int> topVolIndices = {...topCallVolIndices, ...topPutVolIndices};

    // Identify Top 5 Call Ratio and Top 5 Put Ratio indices for Hot Strikes mode (Vol > OI)
    final List<MapEntry<int, double>> callRatioList = [];
    final List<MapEntry<int, double>> putRatioList = [];

    for (int i = 0; i < chartData.length; i++) {
      final item = chartData[i];
      final cVol = (item['call_vol'] ?? 0 as num).toDouble();
      final cOi = (item['call_oi'] ?? 0 as num).toDouble();

      final pVol = (item['put_vol'] ?? 0 as num).toDouble();
      final pOi = (item['put_oi'] ?? 0 as num).toDouble();

      // Calculate Ratio. Avoid division by zero.
      double cRatio = 0;
      if (cOi > 0)
        cRatio = cVol / cOi;
      else if (cVol > 0)
        cRatio = 999; // Infinite ratio if new OI

      double pRatio = 0;
      if (pOi > 0)
        pRatio = pVol / pOi;
      else if (pVol > 0)
        pRatio = 999;

      // Only consider significant activity (e.g., vol > 100 to avoid noise)?
      // For now, raw ratio is requested.

      callRatioList.add(MapEntry(i, cRatio));
      putRatioList.add(MapEntry(i, pRatio));
    }

    callRatioList.sort((a, b) => b.value.compareTo(a.value));
    putRatioList.sort((a, b) => b.value.compareTo(a.value));

    final Set<int> topCallRatioIndices = callRatioList
        .take(5)
        .map((e) => e.key)
        .toSet();
    final Set<int> topPutRatioIndices = putRatioList
        .take(5)
        .map((e) => e.key)
        .toSet();
    final Set<int> topHotIndices = {
      ...topCallRatioIndices,
      ...topPutRatioIndices,
    };

    return Column(
      children: [
        const SizedBox(height: 20),
        Text(
          "Spot: \$${spot.toStringAsFixed(2)}",
          style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 10),
        SingleChildScrollView(
          scrollDirection: Axis.horizontal,
          child: ToggleButtons(
            isSelected: [
              _chartMode == 0,
              _chartMode == 1,
              _chartMode == 2,
              _chartMode == 3,
              _chartMode == 4,
              _chartMode == 5,
            ],
            onPressed: (idx) {
              setState(() {
                _chartMode = idx;
              });
            },
            children: const [
              Padding(
                padding: EdgeInsets.symmetric(horizontal: 12),
                child: Text("Net GEX"),
              ),
              Padding(
                padding: EdgeInsets.symmetric(horizontal: 12),
                child: Text("Call/Put Split"),
              ),
              Padding(
                padding: EdgeInsets.symmetric(horizontal: 12),
                child: Text("Open Interest"),
              ),
              Padding(
                padding: EdgeInsets.symmetric(horizontal: 12),
                child: Text("Absolute Gamma"),
              ),
              Padding(
                padding: EdgeInsets.symmetric(horizontal: 12),
                child: Text("Top Volume"),
              ),
              Padding(
                padding: EdgeInsets.symmetric(horizontal: 12),
                child: Text("Hot Strikes (Vol/OI)"),
              ),
            ],
          ),
        ),
        const SizedBox(height: 20),
        if (resistanceIndex != null)
          Text(
            "Resistance (Call Wall): ${chartData[resistanceIndex]['strike']}",
            style: const TextStyle(color: Colors.redAccent, fontSize: 12),
          ),
        if (supportIndex != null)
          Text(
            "Support (Put Wall): ${chartData[supportIndex]['strike']}",
            style: const TextStyle(color: Colors.greenAccent, fontSize: 12),
          ),
        const SizedBox(height: 10),
        SizedBox(
          height: 350,
          child: BarChart(
            key: ValueKey(_chartMode), // Force rebuild when chart mode changes
            BarChartData(
              barTouchData: BarTouchData(
                enabled:
                    false, // Disable touch interaction to keep tooltips static
                touchTooltipData: BarTouchTooltipData(
                  tooltipBgColor: Colors.transparent,
                  tooltipPadding: EdgeInsets.zero,
                  tooltipMargin: 4,
                  getTooltipItem: (group, groupIndex, rod, rodIndex) {
                    return BarTooltipItem(
                      rod.toY.abs().toStringAsFixed(0),
                      TextStyle(
                        color:
                            (_chartMode == 3 ||
                                _chartMode == 4 ||
                                _chartMode == 5)
                            ? Colors.white
                            : (rodIndex == 0
                                  ? Colors.greenAccent
                                  : Colors.redAccent),
                        fontWeight: FontWeight.bold,
                        fontSize: 10,
                      ),
                    );
                  },
                ),
              ),
              gridData: const FlGridData(show: true, drawVerticalLine: false),
              extraLinesData: ExtraLinesData(
                verticalLines: [
                  if (resistanceIndex != null)
                    VerticalLine(
                      x: resistanceIndex.toDouble(),
                      color: Colors.redAccent,
                      strokeWidth: 3,
                      label: VerticalLineLabel(
                        show: true,
                        alignment: Alignment.topCenter,
                        padding: const EdgeInsets.only(bottom: 5),
                        style: const TextStyle(
                          color: Colors.redAccent,
                          fontWeight: FontWeight.w900,
                          fontSize: 10,
                        ),
                        labelResolver: (line) => "Res",
                      ),
                    ),
                  if (supportIndex != null)
                    VerticalLine(
                      x: supportIndex.toDouble(),
                      color: Colors.greenAccent,
                      strokeWidth: 3,
                      label: VerticalLineLabel(
                        show: true,
                        alignment: Alignment.bottomCenter,
                        padding: const EdgeInsets.only(top: 5),
                        style: const TextStyle(
                          color: Colors.greenAccent,
                          fontWeight: FontWeight.w900,
                          fontSize: 10,
                        ),
                        labelResolver: (line) => "Sup",
                      ),
                    ),
                ],
              ),
              borderData: FlBorderData(show: false),
              titlesData: FlTitlesData(
                topTitles: const AxisTitles(
                  sideTitles: SideTitles(showTitles: false),
                ),
                rightTitles: const AxisTitles(
                  sideTitles: SideTitles(showTitles: false),
                ),
                bottomTitles: AxisTitles(
                  sideTitles: SideTitles(
                    showTitles: true,
                    getTitlesWidget: (val, meta) {
                      int index = val.toInt();
                      if (index < 0 || index >= chartData.length)
                        return const SizedBox();

                      // Hide label if filtered out in Absolute Gamma or Top Volume mode
                      if (_chartMode == 3 && !topGexIndices.contains(index))
                        return const SizedBox();
                      if (_chartMode == 4 && !topVolIndices.contains(index))
                        return const SizedBox();
                      if (_chartMode == 5 && !topHotIndices.contains(index))
                        return const SizedBox();

                      final strike = (chartData[index]['strike'] as num)
                          .toDouble();
                      final isSpot = (strike - spot).abs() / spot < 0.005;

                      TextStyle style = TextStyle(
                        fontSize: 12,
                        fontStyle: FontStyle.italic,
                        fontWeight: FontWeight.bold,
                        color: Colors.white,
                      );

                      // Highlight Support/Resistance labels
                      if (index == resistanceIndex) {
                        style = const TextStyle(
                          fontSize: 12,
                          fontWeight: FontWeight.w900,
                          color: Colors.redAccent,
                        );
                      } else if (index == supportIndex) {
                        style = const TextStyle(
                          fontSize: 12,
                          fontWeight: FontWeight.w900,
                          color: Colors.greenAccent,
                        );
                      }

                      return Transform.rotate(
                        angle: -0.785, // -45 degrees
                        child: Text(strike.toStringAsFixed(0), style: style),
                      );
                    },
                    reservedSize:
                        100, // Increased specificially to avoid overlap with negative OI labels
                  ),
                ),
              ),
              barGroups: chartData.asMap().entries.map<BarChartGroupData>((
                entry,
              ) {
                int index = entry.key;
                var item = entry.value;
                final net = (item['net_gex'] as num).toDouble();
                final call = (item['call_gex'] as num).toDouble();
                final put = (item['put_gex'] as num).toDouble(); // Negative
                final absGex = (item['abs_gex'] ?? 0 as num).toDouble();
                final callOi = (item['call_oi'] ?? 0 as num).toDouble();
                final putOi = (item['put_oi'] ?? 0 as num).toDouble();
                final callVol = (item['call_vol'] ?? 0 as num).toDouble();
                final putVol = (item['put_vol'] ?? 0 as num).toDouble();

                // Highlight logic
                BorderSide border = BorderSide.none;
                if (index == resistanceIndex || index == supportIndex) {
                  border = const BorderSide(
                    color: Colors.yellowAccent,
                    width: 2,
                  );
                }

                if (_chartMode == 0) {
                  return BarChartGroupData(
                    x: index,
                    showingTooltipIndicators: const [],
                    barRods: [
                      BarChartRodData(
                        toY: net,
                        color: net >= 0 ? Colors.greenAccent : Colors.redAccent,
                        width: 12,
                        borderRadius: BorderRadius.circular(2),
                        borderSide: border,
                      ),
                    ],
                  );
                } else if (_chartMode == 1) {
                  return BarChartGroupData(
                    x: index,
                    showingTooltipIndicators: const [],
                    barRods: [
                      BarChartRodData(
                        toY: call,
                        color: Colors.green.withOpacity(0.8),
                        width: 6,
                        borderSide: index == resistanceIndex
                            ? border
                            : BorderSide.none,
                      ),
                      BarChartRodData(
                        toY: put,
                        color: Colors.red.withOpacity(0.8),
                        width: 6,
                        borderSide: index == supportIndex
                            ? border
                            : BorderSide.none,
                      ),
                    ],
                  );
                } else if (_chartMode == 2) {
                  // Open Interest Mode
                  List<int> showingTooltipIndicators = [];
                  if (topCallIndices.contains(index))
                    showingTooltipIndicators.add(0);
                  if (topPutIndices.contains(index))
                    showingTooltipIndicators.add(1);

                  return BarChartGroupData(
                    x: index,
                    showingTooltipIndicators: showingTooltipIndicators,
                    barRods: [
                      BarChartRodData(
                        toY: callOi,
                        color: Colors.green.withOpacity(0.8),
                        width: 6,
                        borderSide: index == resistanceIndex
                            ? border
                            : BorderSide.none,
                      ),
                      BarChartRodData(
                        toY: -putOi, // Render negative for symmetry
                        color: Colors.red.withOpacity(0.8),
                        width: 6,
                        borderSide: index == supportIndex
                            ? border
                            : BorderSide.none,
                      ),
                    ],
                  );
                } else if (_chartMode == 3) {
                  // Absolute Gamma (_chartMode == 3)
                  // Only show top 5 call and top 5 put strikes
                  if (!topGexIndices.contains(index)) {
                    return BarChartGroupData(x: index, barRods: []);
                  }

                  return BarChartGroupData(
                    x: index,
                    showingTooltipIndicators: [0],
                    barRods: [
                      BarChartRodData(
                        toY: absGex,
                        color: topCallGexIndices.contains(index)
                            ? Colors.greenAccent
                            : Colors.redAccent,
                        width: 12,
                        borderRadius: BorderRadius.circular(4),
                      ),
                    ],
                  );
                } else if (_chartMode == 4) {
                  // Top Volume (_chartMode == 4)
                  if (!topVolIndices.contains(index)) {
                    return BarChartGroupData(x: index, barRods: []);
                  }

                  List<BarChartRodData> rods = [];
                  if (topCallVolIndices.contains(index)) {
                    rods.add(
                      BarChartRodData(
                        toY: callVol,
                        color: Colors.greenAccent,
                        width: 8,
                        borderRadius: BorderRadius.circular(4),
                      ),
                    );
                  }
                  if (topPutVolIndices.contains(index)) {
                    rods.add(
                      BarChartRodData(
                        toY: putVol,
                        color: Colors.redAccent,
                        width: 8,
                        borderRadius: BorderRadius.circular(4),
                      ),
                    );
                  }

                  return BarChartGroupData(
                    x: index,
                    showingTooltipIndicators: [0, 1].take(rods.length).toList(),
                    barRods: rods,
                  );
                } else {
                  // Hot Strikes (_chartMode == 5)
                  if (!topHotIndices.contains(index)) {
                    return BarChartGroupData(x: index, barRods: []);
                  }

                  // Recalculate ratios for display height
                  final item = chartData[index];
                  final cVol = (item['call_vol'] ?? 0 as num).toDouble();
                  final cOi = (item['call_oi'] ?? 0 as num).toDouble();
                  final pVol = (item['put_vol'] ?? 0 as num).toDouble();
                  final pOi = (item['put_oi'] ?? 0 as num).toDouble();

                  double cRatio = (cOi > 0)
                      ? cVol / cOi
                      : (cVol > 0 ? 10.0 : 0);
                  double pRatio = (pOi > 0)
                      ? pVol / pOi
                      : (pVol > 0 ? 10.0 : 0);

                  List<BarChartRodData> rods = [];
                  if (topCallRatioIndices.contains(index)) {
                    rods.add(
                      BarChartRodData(
                        toY: cRatio,
                        color: Colors.greenAccent,
                        width: 8,
                        borderRadius: BorderRadius.circular(4),
                      ),
                    );
                  }
                  if (topPutRatioIndices.contains(index)) {
                    rods.add(
                      BarChartRodData(
                        toY: pRatio,
                        color: Colors.redAccent,
                        width: 8,
                        borderRadius: BorderRadius.circular(4),
                      ),
                    );
                  }

                  return BarChartGroupData(
                    x: index,
                    showingTooltipIndicators: [0, 1].take(rods.length).toList(),
                    barRods: rods,
                  );
                }
              }).toList(),
            ),
            swapAnimationDuration: Duration.zero,
          ),
        ),
      ],
    );
  }
}
