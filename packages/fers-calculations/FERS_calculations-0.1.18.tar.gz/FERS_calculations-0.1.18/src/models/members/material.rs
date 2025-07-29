#![allow(non_snake_case)]

use serde::{Deserialize, Serialize};
use utoipa::ToSchema;

#[derive(Serialize, Deserialize, ToSchema, Debug)]
pub struct Material {
    pub id: u32,
    pub name: String,
    pub eMod: f64,
    pub gMod: f64,
    pub density: f64,
    pub yieldStress: f64,
}
