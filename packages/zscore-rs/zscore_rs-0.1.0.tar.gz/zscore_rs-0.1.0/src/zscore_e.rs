use super::stats::{biweight_location, median};
use super::Error;

/// Z-score result containing outlier information
#[derive(Clone, Debug)]
pub struct ZScoreEResult {
    pub outlier_indices: Vec<usize>,
    pub deviations: Vec<f64>,
    pub upper_limit: f64,
    pub lower_limit: f64,
}

impl ZScoreEResult {
    /// Returns the indices of detected outliers
    pub fn outlier_indices(&self) -> &[usize] {
        &self.outlier_indices
    }

    /// Returns the deviations for all points
    pub fn deviations(&self) -> &[f64] {
        &self.deviations
    }

    /// Returns the upper threshold used for outlier detection
    pub fn upper_limit(&self) -> f64 {
        self.upper_limit
    }

    /// Returns the lower threshold used for outlier detection
    pub fn lower_limit(&self) -> f64 {
        self.lower_limit
    }

    /// Returns whether each point is an outlier
    pub fn is_outlier(&self) -> Vec<bool> {
        let mut result = vec![false; self.deviations.len()];
        for &idx in &self.outlier_indices {
            if idx < result.len() {
                result[idx] = true;
            }
        }
        result
    }
}

/// Parameters for Z-Score E algorithm
#[derive(Clone, Debug)]
pub struct ZScoreEParams {
    pub window_percent: f64,
    pub threshold_multiplier: f64,
    pub factor: f64,
}

impl ZScoreEParams {
    /// Create new parameters with default values
    pub fn new() -> Self {
        Self {
            window_percent: 0.1,
            threshold_multiplier: 3.0,
            factor: 1.2533,
        }
    }

    /// Set the window size as a percentage of the data length
    pub fn window_percent(&mut self, percent: f64) -> &mut Self {
        self.window_percent = percent;
        self
    }

    /// Set the threshold multiplier (default: 3.0)
    pub fn threshold_multiplier(&mut self, multiplier: f64) -> &mut Self {
        self.threshold_multiplier = multiplier;
        self
    }

    /// Set the factor for MAD scaling (default: 1.2533)
    pub fn factor(&mut self, factor: f64) -> &mut Self {
        self.factor = factor;
        self
    }

    /// Detect outliers using sliding window biweight location
    pub fn detect_outliers(&self, data: &[f64]) -> Result<ZScoreEResult, Error> {
        if data.is_empty() {
            return Err(Error::Data("Input data is empty".to_string()));
        }

        if self.window_percent <= 0.0 || self.window_percent > 1.0 {
            return Err(Error::Parameter(
                "Window percent must be between 0 and 1".to_string(),
            ));
        }

        let n = data.len();
        let window_size = ((n as f64 * self.window_percent) as usize).max(3);
        let half_window = window_size / 2;

        let mut deviations = Vec::with_capacity(n);

        for i in 0..n {
            let (start_idx, end_idx) = if i < half_window {
                (0, (i + half_window + 1).min(n))
            } else if i > n - half_window - 1 {
                ((i - half_window).max(0), n)
            } else {
                (i - half_window, i + half_window + 1)
            };

            let window = &data[start_idx..end_idx];
            let biweight_loc = biweight_location(window, None)?;
            let deviation = data[i] - biweight_loc;
            deviations.push(deviation);
        }

        let med = median(&deviations)?;

        let mean_abs_dev: f64 =
            deviations.iter().map(|&d| (d - med).abs()).sum::<f64>() / deviations.len() as f64;

        let threshold = self.threshold_multiplier * self.factor * mean_abs_dev;
        let upper_limit = med + threshold;
        let lower_limit = med - threshold;

        let mut outlier_indices = Vec::new();
        for (i, &deviation) in deviations.iter().enumerate() {
            if deviation > upper_limit || deviation < lower_limit {
                outlier_indices.push(i);
            }
        }

        Ok(ZScoreEResult {
            outlier_indices,
            deviations,
            upper_limit,
            lower_limit,
        })
    }
}

impl Default for ZScoreEParams {
    fn default() -> Self {
        Self::new()
    }
}

/// Convenience function for outlier detection with default parameters
#[allow(dead_code)]
pub fn detect_outliers_e(data: &[f64]) -> Result<ZScoreEResult, Error> {
    ZScoreEParams::new().detect_outliers(data)
}

/// Convenience function for outlier detection with custom window percent
pub fn detect_outliers_e_with_window(
    data: &[f64],
    window_percent: f64,
) -> Result<ZScoreEResult, Error> {
    ZScoreEParams::new()
        .window_percent(window_percent)
        .detect_outliers(data)
}

#[cfg(test)]
mod tests {
    use super::*;

    fn generate_test_data() -> Vec<f64> {
        vec![
            1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 100.0, 11.0, 12.0, 13.0, 14.0, 15.0,
            16.0, 17.0, 18.0, 19.0, 20.0,
        ]
    }

    #[test]
    fn test_zscore_e_basic() {
        let data = generate_test_data();
        let result = detect_outliers_e(&data).unwrap();

        // Should detect at least one outlier
        assert!(!result.outlier_indices.is_empty());
        assert_eq!(result.deviations.len(), data.len());
    }

    #[test]
    fn test_zscore_e_with_custom_params() {
        let data = generate_test_data();
        let result = ZScoreEParams::new()
            .window_percent(0.2)
            .threshold_multiplier(2.0)
            .detect_outliers(&data)
            .unwrap();

        assert_eq!(result.deviations.len(), data.len());
        assert!(result.upper_limit > result.lower_limit);
    }

    #[test]
    fn test_zscore_e_empty_data() {
        let data: Vec<f64> = vec![];
        let result = detect_outliers_e(&data);
        assert!(result.is_err());
    }

    #[test]
    fn test_zscore_e_single_value() {
        let data = vec![5.0];
        let result = detect_outliers_e(&data).unwrap();
        assert_eq!(result.deviations.len(), 1);
        assert_eq!(result.deviations[0], 0.0);
    }

    #[test]
    fn test_is_outlier_mask() {
        let data = generate_test_data();
        let result = detect_outliers_e(&data).unwrap();
        let mask = result.is_outlier();

        assert_eq!(mask.len(), data.len());
        for &idx in result.outlier_indices() {
            assert!(mask[idx]);
        }
    }
}
