## Project Summary for Next Claude Agent

### Goal
Develop and evaluate traditional ML models (Logistic Regression, Random Forest) for **F1 safety car prediction** using Catch22 temporal feature extraction. This is part of a larger time series classification research project.

### Technical Context
- **Data Source**: F1 telemetry via custom `f1_etl` library 
- **Target**: Predict safety car deployments from track status (`['green', 'red', 'safety_car', 'vsc', 'vsc_ending', 'yellow']`)
- **Feature Extraction**: Aeon's Catch22Classifier for automatic temporal feature generation
- **Data Format**: Raw telemetry → 3D time series `(n_samples, n_timesteps, n_features)` → Catch22 features → 2D `(n_samples, 22_features)`

### Key Challenge: Severe Class Imbalance
- **~82% "green" flag** (normal racing)
- **<1% "safety_car"** (target class) - only ~128 samples out of 18,300
- **Imbalance ratio**: ~93:1
- Current models barely beat dummy classifier (F1-macro ~0.22)

### Experimental Design Matrix
Test **4 data scopes** × **3 window configurations** = 12 experiments:

**Data Scopes:**
1. `one_session_one_driver` - Single race, single driver (minimal data)
2. `whole_season_one_driver` - All 2024 races, single driver  
3. `one_session_all_drivers` - Single race, all drivers
4. `whole_season_all_drivers` - All 2024 races, all drivers (maximum data)

**Window Configurations:**
- `(window=200, horizon=10)` - Large context, short prediction
- `(window=300, horizon=15)` - Maximum context, medium prediction  
- `(window=250, horizon=20)` - Balanced context, longer prediction

### Current Implementation Status
✅ **Working pipeline** - `SafetyCarEvaluator` class handles:
- Driver mapping (`VER` → `'1'`, etc.)
- Data generation via `f1_etl.create_safety_car_dataset()`  
- Model training with Catch22 feature extraction
- Class imbalance handling (`class_weight='balanced'`)

✅ **Models implemented:**
- `DummyClassifier` (baseline)
- `Catch22Classifier` with `LogisticRegression`
- `Catch22Classifier` with `RandomForest`

### Immediate Next Steps
1. **Run full experimental matrix** - `evaluator.run_all_experiments()`
2. **Address class imbalance** - Consider SMOTE, different thresholds, or cost-sensitive learning
3. **Try different tracks** - Monaco may not have enough safety car events
4. **Optimize window sizes** - Smaller windows = more samples but less context
5. **Add evaluation metrics** - Focus on safety car recall/precision specifically

### Code Entry Point
```python
evaluator = SafetyCarEvaluator(cache_dir="./f1_cache")
evaluator.run_all_experiments()  # Runs all 48 experiments
summary_df = evaluator.generate_summary_report()
```

### Success Criteria
- **Minimum**: F1-macro > 0.3 (beating current ~0.22)
- **Target**: Safety car F1 > 0.1 (currently 0.0)
- **Stretch**: Actionable precision/recall trade-offs for race operations

The foundation is solid - need to scale experiments and tackle the extreme class imbalance problem.