import pandas as pd
import numpy as np
import os
import open3d as o3d

def filter_and_convert_excel(input_file_path, output_file_path, columns_to_keep):
    try:
        # Ensure the output file is not open elsewhere
        if os.path.exists(output_file_path):
            try:
                os.remove(output_file_path)
            except PermissionError:
                print(f"Error: Cannot overwrite '{output_file_path}'. Please close the file.")
                return

        # Read drone data from Excel
        df = pd.read_excel(input_file_path)

        print("Actual Columns in Excel:", df.columns.tolist())

        # Clean column names
        df.columns = df.columns.str.strip()

        # Check for missing columns
        missing_columns = [col for col in columns_to_keep if col not in df.columns]
        if missing_columns:
            print(f"Warning: Missing columns: {missing_columns}")

        # Filter needed columns
        filtered_df = df[[col for col in columns_to_keep if col in df.columns]].copy()

        # Time conversion
        time_col = 'time(millisecond)'
        if time_col in filtered_df.columns:
            filtered_df[time_col] /= 1000
            filtered_df.rename(columns={time_col: 'time(seconds)'}, inplace=True)

        # Height conversion
        height_col = 'height_above_takeoff(feet)'
        if height_col in filtered_df.columns:
            filtered_df[height_col] = (filtered_df[height_col] * 0.3048).round(4)
            filtered_df.rename(columns={height_col: 'height_above_takeoff(meters)'}, inplace=True)

        # Speed conversion
        speed_cols = ['xSpeed(mph)', 'ySpeed(mph)', 'zSpeed(mph)']
        for col in speed_cols:
            if col in filtered_df.columns:
                filtered_df[col] = (filtered_df[col] * 0.44704).round(4)
                filtered_df.rename(columns={col: col.replace('(mph)', '(m/s)')}, inplace=True)

        # Add X, Y, Z
        filtered_df['x(m)'] = 0.0
        filtered_df['y(m)'] = 0.0
        filtered_df['z(m)'] = filtered_df['height_above_takeoff(meters)']

        dt = filtered_df['time(seconds)'].diff().fillna(0)
        filtered_df['x(m)'] = (filtered_df['xSpeed(m/s)'] * dt).cumsum().round(3)
        filtered_df['y(m)'] = (filtered_df['ySpeed(m/s)'] * dt).cumsum().round(3)

        # Read LiDAR data from Excel (assume aligned row-by-row)
        lidar_file_path = "testlidar.xlsx"
        lidar_df = pd.read_excel(lidar_file_path)
        lidar_df.columns = ['Timestamp', 'Distance (cm)']
        lidar_df['Distance (m)'] = lidar_df['Distance (cm)'] / 100

        # Align data by index (truncate to shortest length)
        min_length = min(len(filtered_df), len(lidar_df))
        filtered_df = filtered_df.iloc[:min_length].reset_index(drop=True)
        lidar_df = lidar_df.iloc[:min_length].reset_index(drop=True)

        # Calculate calibrated z directly (row-by-row)
        filtered_df['calibrated_z(m)'] = filtered_df['z(m)'] - lidar_df['Distance (m)']
        filtered_df['altitude(m)'] = filtered_df['calibrated_z(m)'] + 57

        # Drop columns if needed
        filtered_df.drop(columns=['z(m)'], inplace=True)

        # Save processed CSV
        filtered_df.to_csv(output_file_path, index=False)
        print(f"Output CSV file created at: {output_file_path}")

        # Save XYZ
        xyz_df = filtered_df[['x(m)', 'y(m)', 'calibrated_z(m)']].copy()
        xyz_df.rename(columns={'x(m)': 'x', 'y(m)': 'y', 'calibrated_z(m)': 'z'}, inplace=True)

        xyz_output_path = output_file_path.replace('.csv', '_xyz.csv')
        xyz_df.to_csv(xyz_output_path, index=False)
        print(f"XYZ output CSV file created at: {xyz_output_path}")

        # Generate point cloud
        xyz_data = pd.read_csv(xyz_output_path).values
        pcd = o3d.geometry.PointCloud()
        pcd.points = o3d.utility.Vector3dVector(xyz_data)

        vis = o3d.visualization.Visualizer()
        vis.create_window()
        vis.add_geometry(pcd)

        opt = vis.get_render_option()
        opt.background_color = np.array([0.1, 0.1, 0.1])
        opt.point_size = 5.0

        vis.run()
        vis.destroy_window()

    except FileNotFoundError:
        print(f"Error: File '{input_file_path}' or 'lidar_log.xlsx' not found.")
    except PermissionError:
        print(f"Error: Permission denied for '{output_file_path}'. Close any open files.")
    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage
if __name__ == "__main__":
    input_file_path = 'testdata.xlsx'
    output_file_path = 'output_data.csv'
    columns_to_keep = [
        'time(millisecond)', 'datetime(utc)', 'height_above_takeoff(feet)', 
        'xSpeed(mph)', 'ySpeed(mph)', 'zSpeed(mph)'
    ]

    filter_and_convert_excel(input_file_path, output_file_path, columns_to_keep)
