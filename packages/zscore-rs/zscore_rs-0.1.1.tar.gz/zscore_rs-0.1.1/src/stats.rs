use super::Error;

/// Calculate the median of a slice
pub fn median(data: &[f64]) -> Result<f64, Error> {
    if data.is_empty() {
        return Err(Error::Data(
            "Cannot compute median of empty data".to_string(),
        ));
    }

    let mut sorted = data.to_vec();
    sorted.sort_by(|a, b| a.partial_cmp(b).unwrap_or(std::cmp::Ordering::Equal));

    let n = sorted.len();
    if n % 2 == 1 {
        Ok(sorted[n / 2])
    } else {
        Ok((sorted[n / 2 - 1] + sorted[n / 2]) / 2.0)
    }
}

/// Calculate the Median Absolute Deviation (MAD)
pub fn mad(data: &[f64], center: Option<f64>) -> Result<f64, Error> {
    if data.is_empty() {
        return Err(Error::Data("Cannot compute MAD of empty data".to_string()));
    }

    let med = center.unwrap_or(median(data)?);
    let deviations: Vec<f64> = data.iter().map(|x| (x - med).abs()).collect();
    median(&deviations)
}

/// Calculate the mean of a slice
#[allow(dead_code)]
pub fn mean(data: &[f64]) -> Result<f64, Error> {
    if data.is_empty() {
        return Err(Error::Data("Cannot compute mean of empty data".to_string()));
    }

    Ok(data.iter().sum::<f64>() / data.len() as f64)
}

/// Calculate the biweight location (robust estimate of central tendency)
/// Based on Tukey's biweight function
pub fn biweight_location(data: &[f64], c: Option<f64>) -> Result<f64, Error> {
    if data.is_empty() {
        return Err(Error::Data(
            "Cannot compute biweight location of empty data".to_string(),
        ));
    }

    if data.len() == 1 {
        return Ok(data[0]);
    }

    let c = c.unwrap_or(6.0);
    let med = median(data)?;
    let mad_val = mad(data, Some(med))?;

    if mad_val == 0.0 {
        return Ok(med);
    }

    let mut num = 0.0;
    let mut den = 0.0;

    for &x in data {
        let u = (x - med) / (c * mad_val);
        if u.abs() < 1.0 {
            let weight = (1.0 - u * u).powi(2);
            num += x * weight;
            den += weight;
        }
    }

    if den == 0.0 {
        Ok(med)
    } else {
        Ok(num / den)
    }
}

/// Calculate exponential weighted moving average
pub fn ewma(data: &[f64], span: usize, adjust: bool) -> Result<Vec<f64>, Error> {
    if data.is_empty() {
        return Err(Error::Data("Cannot compute EWMA of empty data".to_string()));
    }

    if span == 0 {
        return Err(Error::Parameter("Span must be greater than 0".to_string()));
    }

    let alpha = 2.0 / (span as f64 + 1.0);
    let mut result = Vec::with_capacity(data.len());

    result.push(data[0]);

    if adjust {
        for i in 1..data.len() {
            let numer = data[..=i]
                .iter()
                .enumerate()
                .map(|(j, &x)| x * (1.0 - alpha).powi((i - j) as i32))
                .sum::<f64>();

            let denom = (0..=i)
                .map(|j| (1.0 - alpha).powi((i - j) as i32))
                .sum::<f64>();

            result.push(numer / denom);
        }
    } else {
        for i in 1..data.len() {
            let prev = result[i - 1];
            result.push(alpha * data[i] + (1.0 - alpha) * prev);
        }
    }

    Ok(result)
}

#[cfg(test)]
mod tests {
    use super::*;

    fn assert_approx_eq(a: f64, b: f64, epsilon: f64) {
        assert!((a - b).abs() < epsilon, "Expected {}, got {}", a, b);
    }

    #[test]
    fn test_median() {
        assert_approx_eq(median(&[1.0, 2.0, 3.0]).unwrap(), 2.0, 1e-10);
        assert_approx_eq(median(&[1.0, 2.0, 3.0, 4.0]).unwrap(), 2.5, 1e-10);
        assert_approx_eq(median(&[3.0, 1.0, 2.0]).unwrap(), 2.0, 1e-10);
    }

    #[test]
    fn test_mad() {
        let data = vec![1.0, 2.0, 3.0, 4.0, 5.0];
        let result = mad(&data, None).unwrap();
        assert_approx_eq(result, 1.0, 1e-10);
    }

    #[test]
    fn test_mean() {
        assert_approx_eq(mean(&[1.0, 2.0, 3.0]).unwrap(), 2.0, 1e-10);
        assert_approx_eq(mean(&[1.0, 2.0, 3.0, 4.0]).unwrap(), 2.5, 1e-10);
    }

    #[test]
    fn test_biweight_location() {
        let data = vec![1.0, 2.0, 3.0, 4.0, 5.0];
        let result = biweight_location(&data, None).unwrap();
        assert!((result - 3.0).abs() < 0.5);
    }

    #[test]
    fn test_ewma() {
        let data = vec![1.0, 2.0, 3.0, 4.0, 5.0];
        let result = ewma(&data, 3, false).unwrap();
        assert_eq!(result.len(), data.len());
        assert_eq!(result[0], 1.0);
    }
}
