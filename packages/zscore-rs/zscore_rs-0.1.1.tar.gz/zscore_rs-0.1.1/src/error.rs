use std::error;
use std::fmt;

#[derive(Debug, Eq, PartialEq)]
pub enum Error {
    Parameter(String),
    Data(String),
    Computation(String),
}

impl error::Error for Error {}

impl fmt::Display for Error {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        match *self {
            Error::Parameter(ref err) => write!(f, "Parameter error: {}", err),
            Error::Data(ref err) => write!(f, "Data error: {}", err),
            Error::Computation(ref err) => write!(f, "Computation error: {}", err),
        }
    }
}
