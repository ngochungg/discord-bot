import discord
import asyncio

class DropdownBar(discord.ui.View):
    def __init__(self, items, data_client, active_items, toggle_callback):
        """
        :param items: The full list of objects to display in the dropdown
        :param data_client: The API/Client used to interact with the items (e.g., Docker client)
        :param active_items: A set/list of items currently marked as 'Active' or 'Monitored'
        :param toggle_callback: The function to execute when the toggle button is clicked
        """
        super().__init__(timeout=None)
        self.items = items
        self.data_client = data_client
        
        self.active_items = active_items  if active_items is not None else set()
        
        self.selected_value = None
        self.toggle_logic = toggle_callback
        
        # Initialize specialized Select Menu
        self.add_item(GenericSelect(self.items, self.active_items))
        
        # Add Exit button
        exit_btn = discord.ui.Button(label="Exit", style=discord.ButtonStyle.secondary, row=1)
        exit_btn.callback = self.exit_callback
        self.add_item(exit_btn)
        
    def refresh_ui(self):
        """Update buttons and dropdown based on current state"""
        # Remove dynamic buttons
        for item in list(self.children):
            if isinstance(item, discord.ui.Button) and item.label != "Exit":
                self.remove_item(item)
                
        if self.selected_value:
            # Check if current selection is 'Active'
            is_active = self.selected_value in self.active_items
            label = "Disable" if is_active else "Enable"
            style = discord.ButtonStyle.danger if is_active else discord.ButtonStyle.success
            
            btn = discord.ui.Button(label=label, style=style, row=1)
            btn.callback = self.toggle_callback
            self.add_item(btn)
            
    async def toggle_callback(self, interaction: discord.Interaction):
        """Standard processing flow: Lock -> Execute -> Refresh -> Unlock"""
        for item in self.children: 
            item.disabled = True
        await interaction.response.edit_message(view=self)
        
        # Execute the external logic passed during initialization
        result_state = await self.toggle_logic(self.selected_value)
        
        await asyncio.sleep(1) 
        
        # Unlock and clean up buttons
        for item in list(self.children):
            if isinstance(item, discord.ui.Button) and item.label == "Exit":
                item.disabled = False
            elif isinstance(item, discord.ui.Button):
                self.remove_item(item)
            else:
                item.disabled = False # Enable Select Menu

        # Refresh dropdown emojis
        for item in self.children:
            if isinstance(item, GenericSelect):
                item.update_options(self.active_items)
                
        await interaction.edit_original_response(
            content=f"✅ **{self.selected_value}** is now **{result_state}**.",
            view=self
        )
        self.selected_value = None
        
    async def exit_callback(self, interaction: discord.Interaction):
        self.stop()
        await interaction.response.edit_message(content="🔒 Session closed.", view=None)

class GenericSelect(discord.ui.Select):
    def __init__(self, items, active_items):
        self.items = items
        options = self._build_options(active_items)
        super().__init__(placeholder="Select an item...", options=options, row=0)
    
    def _build_options(self, active_items):
        """Builds list of SelectOptions. Customize 'label' and 'description' attributes here."""
        m_list = active_items if active_items is not None else []
        return [
            discord.SelectOption(
                label=getattr(obj, 'name', str(obj)), # Works for Docker objects or simple strings
                emoji="🟢" if getattr(obj, 'name', str(obj)) in m_list else "🔴",
                description=f"Status: {getattr(obj, 'status', 'Unknown')}"
            ) for obj in self.items
        ]
        
    def update_options(self, active_items):
        self.options = self._build_options(active_items)
        
    async def callback(self, interaction: discord.Interaction):
        self.view.selected_value = self.values[0]
        for opt in self.options: 
            opt.default = (opt.label == self.values[0])
        self.view.refresh_ui()
        await interaction.response.edit_message(view=self.view)