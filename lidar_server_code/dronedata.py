import pandas as pd
import os
import numpy as np
import open3d as o3d
import pandas as pd

def filter_and_convert_csv(input_file_path, output_file_path, columns_to_keep):
    try:
        # Ensure the output file is not open elsewhere
        if os.path.exists(output_file_path):
            try:
                os.remove(output_file_path)  # Delete existing file to avoid access issues
            except PermissionError:
                print(f"Error: Cannot overwrite '{output_file_path}'. Please close the file if it is open.")
                return
        
        # Read the input CSV file
        df = pd.read_csv(input_file_path)

        # Debugging: Print actual column name
        # s
        print("Actual Columns in CSV:", df.columns.tolist())

        # Strip spaces and standardize column names
        df.columns = df.columns.str.strip()

        # Check if the specified columns exist in the DataFrame
        missing_columns = [col for col in columns_to_keep if col not in df.columns]
        if missing_columns:
            print(f"Warning: The following columns are missing: {missing_columns}")

        # Filter the DataFrame to include only the specified columns
        filtered_df = df[[col for col in columns_to_keep if col in df.columns]].copy()

        # Convert time from milliseconds to seconds **in place**
        time_col = 'time(millisecond)'
        if time_col in filtered_df.columns:
            filtered_df[time_col] /= 1000  # Convert to seconds
            filtered_df.rename(columns={time_col: 'time(seconds)'}, inplace=True)  # Rename column

        # Convert height from feet to meters **in place**
        height_col = 'height_above_takeoff(feet)'
        if height_col in filtered_df.columns:
            filtered_df[height_col] = (filtered_df[height_col]*0.3048).round(4)  # Convert to meters
            filtered_df.rename(columns={height_col: 'height_above_takeoff(meters)'}, inplace=True)  # Rename column
        
        speed_cols = ['xSpeed(mph)', 'ySpeed(mph)', 'zSpeed(mph)']
        for col in speed_cols:
            if col in filtered_df.columns:
                filtered_df[col] = (filtered_df[col] * 0.44704).round(4)  # Convert and round
                filtered_df.rename(columns={col: col.replace('(mph)', '(m/s)')}, inplace=True)
        
        filtered_df['x(m)'] = 0.0
        filtered_df['y(m)'] = 0.0
        filtered_df['z(m)'] = filtered_df['height_above_takeoff(meters)']

        dt = filtered_df['time(seconds)'].diff().fillna(0)

        filtered_df['x(m)'] = (filtered_df['xSpeed(m/s)'] * dt).cumsum().round(3)
        filtered_df['y(m)'] = (filtered_df['ySpeed(m/s)'] * dt).cumsum().round(3)

        # Write the processed DataFrame to the output CSV file
        #filtered_df.to_csv(output_file_path, index=False, mode='w')

        #print(f"Output CSV file created successfully at: {output_file_path}")

#LIDAR STUFFFF
        # Read LiDAR data from Excel file
        lidar_file_path = "lidar_log.csv"
        lidar_df = pd.read_csv(lidar_file_path)
        lidar_df.columns = ['Timestamp', 'Distance (cm)'] #ADDED NOW
        # Convert LiDAR Distance from cm to meters
        lidar_df['Distance (m)'] = lidar_df['Distance (cm)'] / 100

        # Ensure timestamps are in datetime format
        lidar_df['Timestamp'] = pd.to_datetime(lidar_df['Timestamp'])
        filtered_df['datetime(utc)'] = pd.to_datetime(filtered_df['datetime(utc)'])

        print(lidar_df['Timestamp'].head(10).tolist())
        
        # Merge drone data with LiDAR data based on nearest timestamp within a 1-second tolerance
        merged_df = pd.merge_asof(
            filtered_df.sort_values('datetime(utc)'),
            lidar_df.sort_values('Timestamp'),
            left_on='datetime(utc)',
            right_on='Timestamp',
            direction='nearest',
            tolerance=pd.Timedelta(seconds=1)
        )

        # Calculate calibrated z-coordinate
        merged_df['calibrated_z(m)'] = merged_df['z(m)'] - merged_df['Distance (m)']

        # Define a constant value to add to the calibrated z for the 'altitude' column
        constant_value = 57  # You can change this constant as needed

        # Create a new column 'altitude' by adding the constant value to 'calibrated_z(m)'
        merged_df['altitude(m)'] = merged_df['calibrated_z(m)'] + constant_value

        # Drop unwanted columns (z(m), Timestamp, Distance (cm)) before saving to CSV
        columns_to_drop = ['z(m)', 'Timestamp', 'Distance (m)','Distance (cm)']
        merged_df.drop(columns=[col for col in columns_to_drop if col in merged_df.columns], inplace=True)

        # Write the processed DataFrame to the output CSV file
        merged_df.to_csv(output_file_path, index=False)

        print(f"Output CSV file created successfully at: {output_file_path}")

        #ADDED CODE
        xyz_df = merged_df[['x(m)', 'y(m)', 'calibrated_z(m)']].copy()
        xyz_df.rename(columns={
            'x(m)': 'x',
            'y(m)': 'y',
            'calibrated_z(m)': 'z'
        }, inplace=True)

        xyz_output_path = output_file_path.replace('.csv', '_xyz.csv')
        xyz_df.to_csv(xyz_output_path, index=False)
        print(f"XYZ output CSV file created successfully at: {xyz_output_path}")
        
                # ✨✨ Now generate a point cloud from xyz_output_path
        xyz_data = pd.read_csv(xyz_output_path).values

        # Create point cloud
        pcd = o3d.geometry.PointCloud()
        pcd.points = o3d.utility.Vector3dVector(xyz_data)

        # Create a visualizer
        vis = o3d.visualization.Visualizer()
        vis.create_window()

        # Add point cloud
        vis.add_geometry(pcd)

        # Get render options
        opt = vis.get_render_option()
        opt.background_color = np.array([0.1, 0.1, 0.1])  # Dark gray background
        opt.point_size = 5.0  # Increase point size

        # Run the visualizer
        vis.run()
        vis.destroy_window()


    except FileNotFoundError:
        print(f"Error: Input file '{input_file_path}' not found.")
    except PermissionError:
        print(f"Error: Permission denied for '{output_file_path}'. Try a different filename or close any open files.")
    except Exception as e:
        print(f"An error occurred: {e}")


# Example usage
if __name__ == "__main__":
    input_file_path = 'inputdata.csv'  # Path to your input CSV file
    output_file_path = 'output_data.csv'  # Changed filename to avoid conflicts
    columns_to_keep = ['time(millisecond)', 'datetime(utc)', 'height_above_takeoff(feet)', 
                       'xSpeed(mph)', 'ySpeed(mph)', 'zSpeed(mph)']  # Columns you want to keep

    filter_and_convert_csv(input_file_path, output_file_path, columns_to_keep)

 
 #CONSIDER OFFSET


