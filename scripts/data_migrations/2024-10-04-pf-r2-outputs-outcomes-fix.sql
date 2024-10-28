-- Update "m2 of heritage buildings renovated/restored" to "m2 of Heritage buildings renovated/restored"
UPDATE output_dim
SET output_name = 'm2 of Heritage buildings renovated/restored'
WHERE output_name = 'm2 of heritage buildings renovated/restored';

-- Update "Amount of Floor Space Ratinalised (Sqm)" to "Amount of Floor Space Rationalised (Sqm)"
UPDATE output_dim
SET output_name = 'Amount of Floor Space Rationalised (Sqm)'
WHERE output_name = 'Amount of Floor Space Ratinalised (Sqm)';

-- Update "number of cleared sites" to "Number of cleared sites"
UPDATE output_dim
SET output_name = 'Number of cleared sites'
WHERE output_name = 'number of cleared sites';
