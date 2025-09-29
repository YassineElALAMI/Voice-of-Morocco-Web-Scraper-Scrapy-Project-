class VoiceOfMoroccoPipeline:
    def process_item(self, item, spider):
        # Clean text: remove extra whitespace/newlines
        if item.get("text"):
            item["text"] = " ".join(item["text"].split())

        # Ensure images/videos/links are unique while preserving order
        def _unique_preserve_order(seq):
            if not seq:
                return seq
            seen = set()
            out = []
            for x in seq:
                if x in seen:
                    continue
                seen.add(x)
                out.append(x)
            return out

        if item.get("images"):
            item["images"] = _unique_preserve_order(item["images"])
        if item.get("videos"):
            item["videos"] = _unique_preserve_order(item["videos"])
        if item.get("links"):
            item["links"] = _unique_preserve_order(item["links"])

        return item
